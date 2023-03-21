import os
from selenium import webdriver
# from selenium.webdriver.common.by import By
from utils import write_to_file

# load environment variables
from dotenv import load_dotenv
load_dotenv()

OS_NAME = os.getenv('OS')
CHIPSET = os.getenv('CHIPSET')

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
        driver_path = ''
        if OS_NAME == 'Windows_NT':
            if browser_name == 'chrome':
                driver_path = 'chrome_drivers/chromedriver_win32/chromedriver.exe'
            else:
                driver_path = 'edge_drivers/edgedriver_win64/msedgedriver.exe'
        elif OS_NAME == 'Linux':
            driver_path = 'chrome_drivers/chromedriver_linux64/chromedriver'
        elif OS_NAME == 'MacOS':
            # TODO: what happens if .env variable is missing?
            if CHIPSET == 'M1':
                driver_path = 'edge_drivers/edgedriver_mac64_m1/msedgedriver'
            else:
                driver_path = 'edge_drivers/edgedriver_mac64/msedgedriver'
                driver_path = 'chrome_drivers/chromedriver_mac64/chromedriver'
        else:
            print(f'OS {OS_NAME} not supported')
            return None

        driver_path = f'web_drivers/{driver_path}'
        return os.path.join(os.path.dirname(__file__), driver_path)

    # no OS name found
    return os.getenv('CHROME_DRIVER_PATH')


CHROME_DRIVER_PATH = get_driver_exact_location('chrome')
EDGE_DRIVER_PATH = get_driver_exact_location('edge')


def build_driver(link=None, chrome_driver=CHROME_DRIVER_PATH, edge_driver=EDGE_DRIVER_PATH):
    # check for edge driver
    # docs: https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/?tabs=c-sharp
    try:
        options = webdriver.EdgeOptions()
        options.add_argument("headless") # list of strings

        driver = webdriver.Edge(edge_driver, options=options)
        # service = Service(verbose = True)
        # driver = webdriver.Edge(service=service)
    except:
        print('Edge driver not found')

        options = webdriver.ChromeOptions()

        # for heroku use this:
        # chrome_bin = os.getenv("GOOGLE_CHROME_BIN")
        # if chrome_bin:
        #     options.binary_location = chrome_bin
        #     options.add_argument("--disable-dev-shm-usage")
        #     options.add_argument("--no-sandbox")

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')

        options.add_argument("--headless")
        options.add_argument("--window-size=%s" % WINDOW_SIZE)
        options.add_argument('--log-level=1')

        driver = webdriver.Chrome(executable_path=chrome_driver, chrome_options=options)

    if link:
        driver.get(link)
    return driver


def get_html_using_selenium(url=None, driver=None):
    if driver is None:
        driver = build_driver()

    if url:
        driver.get(url)

    # handle infinite scroll
    # lenOfPage = driver.execute_script(
    #     "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    # match = False
    # while(match is False):
    #     lastCount = lenOfPage
    #     time.sleep(3)
    #     lenOfPage = driver.execute_script(
    #         "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    #     if lastCount == lenOfPage:
    #         match = True

    # Page is fully scrolled now. Next step is to extract the source code from it.
    my_html = driver.page_source

    # write_to_file(my_html, './json/goodreads_html_2.html')

    driver.quit()

    return my_html
