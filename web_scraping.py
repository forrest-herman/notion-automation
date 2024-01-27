import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
# import chromedriver_autoinstaller

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.service import Service as EdgeService
# from selenium.webdriver.common.by import By
from utils import write_to_file

# load environment variables
from dotenv import load_dotenv
load_dotenv()

OS_NAME = os.getenv('OS')
# TODO: what happens if .env variable is missing?
CHIPSET = os.getenv('CHIPSET')
# print(CHIPSET)

'''
The Selenium package is used to automate web browser interaction with python.
We will use it to open and scroll the webpage in an automated way.

Followed this article: 
https://ankitmodi.github.io/intro-to-web-scraping-using-python-on-goodreads/

Make sure the correct chrome driver is installed https://chromedriver.chromium.org/
'''

WINDOW_SIZE = "1200,1200"


def get_driver_exact_location(browser_name=None):
    if OS_NAME:
        if OS_NAME == 'Windows_NT':
            if browser_name == 'edge':
                driver_path = 'edge_drivers/edgedriver_win64/msedgedriver.exe'
            else:
                driver_path = 'chrome_drivers/chromedriver_win32/chromedriver.exe'
        elif OS_NAME == 'Linux':
            driver_path = 'chrome_drivers/chromedriver_linux64/chromedriver'
        elif OS_NAME == 'MacOS':
            if CHIPSET == 'M1':
                driver_path = 'edge_drivers/edgedriver_mac64_m1/msedgedriver'
            else:
                if browser_name == 'edge':
                    driver_path = 'edge_drivers/edgedriver_mac64/msedgedriver'
                else:
                    driver_path = 'chrome_drivers/chromedriver_mac64/chromedriver'
        else:
            print(f'OS {OS_NAME} not supported')
            return None

        driver_path = f'web_drivers/{driver_path}'
        return os.path.join(os.path.dirname(__file__), driver_path)

    # no OS name found
    return os.getenv('CHROME_DRIVER_PATH')


def build_driver(link:str=None, browser:str='', headless:bool=True):
    if browser:
        driver_path = get_driver_exact_location(browser)
    
    # check for edge driver
    # docs: https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/?tabs=c-sharp
    try:
        if browser == 'edge' or OS_NAME == 'Windows_NT':
            # install and setup chromedriver

            edge_options = EdgeOptions()
            options = [
                "inprivate",
                "--window-size=%s" % WINDOW_SIZE,
                "--log-level=3"
            ]
            if headless:
                options.append("--headless")
            for option in options:
                edge_options.add_argument(option)

            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=edge_options)
        elif browser == 'chrome':
            options = webdriver.ChromeOptions()

            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')

            if headless:
                options.add_argument("--headless")
            options.add_argument("--window-size=%s" % WINDOW_SIZE)
            options.add_argument('--log-level=1')

            driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        else:
            # install and setup chromedriver

            chrome_options = Options()
            options = [
                "--headless",
                "--disable-gpu",
                "--window-size=%s" % WINDOW_SIZE,
                "--ignore-certificate-errors",
                "--disable-extensions",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
            for option in options:
                chrome_options.add_argument(option)

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f'{browser} driver not found', e)
        raise e

    if link:
        driver.get(link)
    return driver


def get_html_using_selenium(url=None, driver=None, infinite_scroll=False):
    if driver is None:
        driver = build_driver()

    if url:
        print(f'Opening url: {url}')
        driver.get(url)

    if infinite_scroll:
        # handle infinite scroll
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match = False
        while(match is False):
            lastCount = lenOfPage
            time.sleep(3)
            lenOfPage = driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount == lenOfPage:
                match = True

    # Page is fully scrolled now. Next step is to extract the source code from it.
    my_html = driver.page_source

    # write_to_file(my_html, './json/goodreads_html_2.html')

    driver.quit()

    return my_html
