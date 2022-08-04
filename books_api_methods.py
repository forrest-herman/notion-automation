import requests
import os

from dotenv import load_dotenv

from utils import save_json_to_file
load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')


def search_book(keywords, title=None, author=None):
    keywords = '+'.join(keywords)
    url = f'https://www.googleapis.com/books/v1/volumes?q={keywords}'

    if author:
        url += f'+inauthor:{author}'
    if title:
        url += f'+intitle:{title}'

    url += '&printType=books'
    url += f'&key={API_KEY}'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code)
        print("search book error", result.text)
        exit()

    return result.json()


book_data = search_book([], title='People We Meet on Vacation', author='Emily Henry')
save_json_to_file(book_data, './json/books_api/test.json')
