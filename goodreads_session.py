"""Selenium sessions that log in only when Goodreads requests it."""

import os
from urllib.parse import urlsplit

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from web_scraping import build_driver, get_html_using_selenium

SIGN_IN_URL = "https://www.goodreads.com/user/sign_in"
SIGNED_IN_SELECTOR = (
    'a[href*="/user/sign_out"], .siteHeader__personal a[href*="/user/show/"]'
)


def wait_for_page_content(driver, timeout=15):
    """Reject blank responses before checking login or parsing reading data."""
    try:
        WebDriverWait(driver, timeout).until(lambda browser: browser.execute_script(
            "return Boolean(document.body && document.body.innerText.trim());"
        ))
    except TimeoutException:
        raise RuntimeError(
            "Goodreads returned an empty page. Login and scraping were stopped. "
            "If this occurs only in headless mode, try another browser or run "
            "with headless=False; on Linux CI, use a virtual display such as Xvfb."
        ) from None


def is_sign_in_page(driver):
    """Recognize login redirects or a visible login form, not header links."""
    location = urlsplit(driver.current_url)
    if location.hostname not in {"goodreads.com", "www.goodreads.com"}:
        return False
    if location.path.rstrip("/") in {"/user/sign_in", "/ap/signin"}:
        return True
    return any(
        element.is_displayed()
        for element in driver.find_elements(
            By.CSS_SELECTOR, "button.authPortalSignInButton, input#ap_email"
        )
    )


def login_goodreads(driver, timeout=20):
    """Sign in with email and wait for authenticated navigation to appear.

    No credentials, cookies, or login-page HTML are logged on failure.
    """
    email = os.getenv("GOODREADS_EMAIL")
    password = os.getenv("GOODREADS_PASSWORD")
    if not email or not password:
        raise ValueError("Set both GOODREADS_EMAIL and GOODREADS_PASSWORD to log in.")

    wait = WebDriverWait(driver, timeout)
    if not is_sign_in_page(driver):
        driver.get(SIGN_IN_URL)
    if driver.find_elements(By.CSS_SELECTOR, SIGNED_IN_SELECTOR):
        return

    try:
        if urlsplit(driver.current_url).path.rstrip("/") != "/ap/signin":
            # Some pages embed the email form instead of showing the chooser.
            entry = wait.until(EC.any_of(
                EC.visibility_of_element_located((By.ID, "ap_email")),
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.authPortalSignInButton")
                ),
            ))
            if entry.get_attribute("id") != "ap_email":
                entry.click()
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "ap_email")))
        email_input.clear()
        email_input.send_keys(email)
        password_input = wait.until(
            EC.visibility_of_element_located((By.ID, "ap_password"))
        )
        password_input.clear()
        password_input.send_keys(password)
        wait.until(EC.element_to_be_clickable((By.ID, "signInSubmit"))).click()
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SIGNED_IN_SELECTOR))
        )
    except TimeoutException:
        raise RuntimeError(
            "Goodreads login did not complete. Check your credentials and whether "
            "Goodreads requires verification or has changed its sign-in page."
        ) from None


def build_goodreads_driver(link=None, browser="", headless=True):
    """Open the target first and log in only if a sign-in page appears."""
    driver = build_driver(browser=browser, headless=headless)
    try:
        driver.get(link or SIGN_IN_URL)
        wait_for_page_content(driver)
        if is_sign_in_page(driver):
            login_goodreads(driver)
            if link and urlsplit(link).path.rstrip("/") not in {
                "/user/sign_in", "/ap/signin"
            }:
                driver.get(link)
                wait_for_page_content(driver)
                if is_sign_in_page(driver):
                    raise RuntimeError("Goodreads still requires login for the requested page.")
        return driver
    except Exception:
        driver.quit()
        raise


def get_goodreads_html(url, infinite_scroll=False):
    """Read a Goodreads page, logging in if needed, then close the browser."""
    driver = build_goodreads_driver(url)
    try:
        # The existing HTML helper closes the browser after a successful read.
        return get_html_using_selenium(
            driver=driver, infinite_scroll=infinite_scroll
        )
    except Exception:
        driver.quit()
        raise
