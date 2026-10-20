from unittest.mock import Mock, call

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

import goodreads_session as sessions

TARGET = "https://www.goodreads.com/review/list/123?shelf=read"


@pytest.fixture
def driver(monkeypatch):
    browser = Mock()
    browser.current_url = TARGET
    browser.find_elements.return_value = []
    monkeypatch.setattr(sessions, "build_driver", Mock(return_value=browser))
    monkeypatch.setattr(sessions, "wait_for_page_content", Mock())
    return browser


@pytest.fixture
def credentials(monkeypatch):
    monkeypatch.setenv("GOODREADS_EMAIL", "reader@example.test")
    monkeypatch.setenv("GOODREADS_PASSWORD", "test-password")


@pytest.mark.parametrize("url,expected", [
    (sessions.SIGN_IN_URL + "?return_to=/review/list/123", True),
    ("https://www.goodreads.com/ap/signin?language=en_US", True),
    ("https://goodreads.com/user/sign_in/", True),
    (TARGET, False),
    ("https://www.goodreads.com/user/show/123", False),
    ("https://www.goodreads.com/book/show/123", False),
    ("https://example.com/user/sign_in", False),
    ("https://goodreads.com.example.com/ap/signin", False),
])
def test_sign_in_detection(driver, url, expected):
    driver.current_url = url
    assert sessions.is_sign_in_page(driver) is expected


@pytest.mark.parametrize("visible", [False, True])
def test_embedded_login_detection(driver, visible):
    element = Mock()
    element.is_displayed.return_value = visible
    driver.find_elements.return_value = [element]
    assert sessions.is_sign_in_page(driver) is visible
    driver.find_elements.assert_called_once_with(
        By.CSS_SELECTOR, "button.authPortalSignInButton, input#ap_email"
    )


def test_public_page_needs_no_credentials_or_login(monkeypatch, driver):
    monkeypatch.delenv("GOODREADS_EMAIL", raising=False)
    monkeypatch.delenv("GOODREADS_PASSWORD", raising=False)
    login = Mock()
    monkeypatch.setattr(sessions, "login_goodreads", login)
    assert sessions.build_goodreads_driver(TARGET) is driver
    driver.get.assert_called_once_with(TARGET)
    login.assert_not_called()


def test_target_opens_before_login_and_is_revisited(monkeypatch, driver):
    events = []
    driver.get.side_effect = lambda url: events.append(url)
    monkeypatch.setattr(sessions, "is_sign_in_page", Mock(side_effect=[True, False]))
    monkeypatch.setattr(sessions, "login_goodreads", Mock(side_effect=lambda browser: events.append("login")))
    assert sessions.build_goodreads_driver(TARGET) is driver
    assert events == [TARGET, "login", TARGET]
    driver.quit.assert_not_called()


def test_repeated_login_redirect_fails_without_looping(monkeypatch, driver):
    monkeypatch.setattr(sessions, "is_sign_in_page", Mock(return_value=True))
    login = Mock()
    monkeypatch.setattr(sessions, "login_goodreads", login)
    with pytest.raises(RuntimeError, match="still requires login"):
        sessions.build_goodreads_driver(TARGET)
    login.assert_called_once_with(driver)
    assert driver.get.call_args_list == [call(TARGET), call(TARGET)]
    driver.quit.assert_called_once()


@pytest.mark.parametrize("missing", ["GOODREADS_EMAIL", "GOODREADS_PASSWORD"])
def test_credentials_required_only_after_login_redirect(monkeypatch, driver, credentials, missing):
    monkeypatch.delenv(missing)
    driver.current_url = sessions.SIGN_IN_URL
    with pytest.raises(ValueError, match="Set both GOODREADS_EMAIL"):
        sessions.build_goodreads_driver(TARGET)
    driver.get.assert_called_once_with(TARGET)
    driver.quit.assert_called_once()


@pytest.mark.parametrize("direct_form", [False, True])
def test_login_submits_form_without_resetting_redirect(monkeypatch, driver, credentials, direct_form):
    driver.current_url = (
        "https://www.goodreads.com/ap/signin?siteState=return-target"
        if direct_form else sessions.SIGN_IN_URL + "?return_to=target"
    )
    chooser, email, password, submit, header = [Mock() for _ in range(5)]
    chooser.get_attribute.return_value = ""
    wait = Mock()
    wait.until.side_effect = ([chooser] if not direct_form else []) + [email, password, submit, header]
    monkeypatch.setattr(sessions, "WebDriverWait", Mock(return_value=wait))
    sessions.login_goodreads(driver)
    driver.get.assert_not_called()
    assert chooser.click.call_count == (0 if direct_form else 1)
    email.clear.assert_called_once()
    email.send_keys.assert_called_once_with("reader@example.test")
    password.clear.assert_called_once()
    password.send_keys.assert_called_once_with("test-password")
    submit.click.assert_called_once()
    probe = Mock()
    wait.until.call_args_list[-1].args[0](probe)
    probe.find_element.assert_called_once_with(By.CSS_SELECTOR, sessions.SIGNED_IN_SELECTOR)


def test_already_signed_in_skips_form(monkeypatch, driver, credentials):
    driver.current_url = sessions.SIGN_IN_URL
    driver.find_elements.return_value = [Mock()]
    wait = Mock()
    monkeypatch.setattr(sessions, "WebDriverWait", Mock(return_value=wait))
    sessions.login_goodreads(driver)
    wait.until.assert_not_called()


@pytest.mark.parametrize("completed_steps", [0, 4])
def test_login_timeout_is_safe_and_closes_browser(monkeypatch, driver, credentials, completed_steps):
    driver.current_url = sessions.SIGN_IN_URL
    wait = Mock()
    wait.until.side_effect = [Mock() for _ in range(completed_steps)] + [
        TimeoutException("sensitive page details")
    ]
    monkeypatch.setattr(sessions, "WebDriverWait", Mock(return_value=wait))
    with pytest.raises(RuntimeError, match="Goodreads login did not complete") as error:
        sessions.build_goodreads_driver(TARGET)
    assert "sensitive page details" not in str(error.value)
    assert "test-password" not in str(error.value)
    driver.quit.assert_called_once()
    driver.get.assert_called_once_with(TARGET)


def test_html_failure_closes_browser(monkeypatch, driver):
    monkeypatch.setattr(sessions, "get_html_using_selenium", Mock(side_effect=RuntimeError("read failed")))
    with pytest.raises(RuntimeError, match="read failed"):
        sessions.get_goodreads_html(TARGET)
    driver.quit.assert_called_once()


def test_html_read_does_not_navigate_past_login_check(monkeypatch, driver):
    read_html = Mock(return_value="<table id='books'></table>")
    monkeypatch.setattr(sessions, "get_html_using_selenium", read_html)
    assert sessions.get_goodreads_html(TARGET, infinite_scroll=True) == read_html.return_value
    driver.get.assert_called_once_with(TARGET)
    read_html.assert_called_once_with(driver=driver, infinite_scroll=True)


def test_blank_page_waits_for_rendered_content(monkeypatch):
    browser = Mock()
    browser.execute_script.side_effect = [False, True]
    sessions.wait_for_page_content(browser, timeout=1)
    assert browser.execute_script.call_count == 2


def test_blank_page_timeout_has_actionable_error(monkeypatch):
    wait = Mock()
    wait.until.side_effect = TimeoutException("sensitive response details")
    monkeypatch.setattr(sessions, "WebDriverWait", Mock(return_value=wait))
    with pytest.raises(RuntimeError, match="Goodreads returned an empty page") as error:
        sessions.wait_for_page_content(Mock())
    assert "sensitive response details" not in str(error.value)


def test_blank_page_stops_before_login_or_scrape(monkeypatch, driver):
    monkeypatch.setattr(sessions, "wait_for_page_content", Mock(side_effect=RuntimeError("empty page")))
    login = Mock()
    read_html = Mock()
    monkeypatch.setattr(sessions, "login_goodreads", login)
    monkeypatch.setattr(sessions, "get_html_using_selenium", read_html)
    with pytest.raises(RuntimeError, match="empty page"):
        sessions.get_goodreads_html(TARGET)
    login.assert_not_called()
    read_html.assert_not_called()
    driver.quit.assert_called_once()
