# import time
from selenium import webdriver
from utils import write_to_file

'''
The Selenium package is used to automate web browser interaction with python.
We will use it to open and scroll the webpage in an automated way.

Followed this article: 
https://ankitmodi.github.io/intro-to-web-scraping-using-python-on-goodreads/
'''

CHROME_DRIVER_PATH = 'D:/PC Files/Documents/GitHub/Python/notion-automation/chromedriver_win32/chromedriver.exe'


def get_html_using_selenium(url, chrome_driver=CHROME_DRIVER_PATH):

    driver = webdriver.Chrome(executable_path=chrome_driver)
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
