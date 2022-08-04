import os
from selenium import webdriver
from utils import write_to_file

# load environment variables
from dotenv import load_dotenv
load_dotenv()

OS_NAME = os.getenv('OS')

'''
The Selenium package is used to automate web browser interaction with python.
We will use it to open and scroll the webpage in an automated way.

Followed this article: 
https://ankitmodi.github.io/intro-to-web-scraping-using-python-on-goodreads/

Make sure the correct chrome driver is installed https://chromedriver.chromium.org/
'''
WINDOW_SIZE = "1200,1200"


def get_chrome_driver_exact_location():
    chrome_driver = ''
    if OS_NAME == 'Windows_NT':
        chrome_driver = 'chromedriver_win32/chromedriver.exe'
    elif OS_NAME == 'Linux':
        chrome_driver = 'chromedriver_linux64/chromedriver'
    elif OS_NAME == 'MacOS':
        chrome_driver = 'chromedriver_mac64/chromedriver'
    else:
        print(f'OS {OS_NAME} not supported')
        exit()

    return f'chromedrivers/{chrome_driver}'


CHROME_DRIVER_PATH = os.path.join(
    os.path.dirname(__file__), get_chrome_driver_exact_location())


def get_html_using_selenium(url, chrome_driver=CHROME_DRIVER_PATH):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    options.add_argument('--log-level=1')
    driver = webdriver.Chrome(executable_path=chrome_driver, chrome_options=options)

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
    driver.quit()

    # write_to_file(my_html, './json/goodreads_html.html')

    return my_html
