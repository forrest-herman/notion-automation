import re
import datetime
from utils import write_to_file
from utils import save_json_to_file
from bs4 import BeautifulSoup
# BeautifulSoup is a python library to scrap data from web pages.

from web_scraping import get_html_using_selenium

URL_HOMEPAGE = 'https://www.goodreads.com/user/show/58061822-forrest-herman'
URL_BOOKS_READ = 'https://www.goodreads.com/review/list/58061822-forrest-herman?order=d&shelf=read&sort=date_read'
URL_CURRENTLY_READING = 'https://www.goodreads.com/review/list/58061822-forrest-herman?order=d&shelf=currently-reading'

OUTPUT_MD_FILE_PATH = 'markdown_file.md'


def get_rating_from_text(rating_text):
    rating_dict = {
        'did not like it': '1',
        'it was ok': '2',
        'liked it': '3',
        'really liked it': '4',
        'it was amazing': '5'
    }
    try:
        rating = rating_dict[rating_text]
    except KeyError:
        rating = None  # avoid issues if the book is unrated
    return rating


def get_progress_from_home_page(url=URL_HOMEPAGE):
    html_str = get_html_using_selenium(url)
    soup = BeautifulSoup(html_str, 'lxml')
    progress = soup.find(class_='graphContainer progressGraph').find(class_='graphBar').get('style')
    progress = re.search(r'width: (\d+)%', progress).group(1)

    return progress  # current progress percentage


def get_books_list_data_from_html(html_str):
    """Check the My Books Feed and parse for all the books details. Such as read dates and author."""
    soup = BeautifulSoup(html_str, 'lxml')

    table = soup.find_all('table', {'id': 'books'})[0]
    table_rows = table.find_all('tr')
    book_list = []

    for tr in table_rows[1:]:
        book_dict = {}

        # book dict format:
        """
        {
            "cover_url": "https://i.gr-assets.com/images/etc.jpg",
            "title": "The Unhoneymooners",
            "series": "Series Name or None",
            "book_url": "/book/show/42201431-the-unhoneymooners",
            "author_name": "Lauren, Christina",
            "author_url": "/author/show/6556689.Christina_Lauren",
            "rating": "3",
            "review": "None",
            "date_started": "Jun 3, 2022"
            "date_read": "Jun 23, 2022"
        }
        """

        # parse cover_url
        td = tr.find_all('td', {'class': 'field cover'})[0]
        img = td.find_all('img')[0]
        book_dict['cover_url'] = img['src']
        # get higher resolution cover
        book_dict['cover_url'] = book_dict['cover_url'].replace(
            '_SX50_.', '').replace('_SY75_.', '')
        # REXEG alternative
        # book_dict['cover_url'] = re.sub(r'_[a-zA-Z0-9]+_.', '', book_dict['cover_url'])

        # parse title, series, and book's url
        td = tr.find_all('td', {'class': 'field title'})[0]
        a_link = td.find_all('a')[0]
        full_title = a_link.get('title')
        # parse title for a series component
        find_series_regex = r"\s+?[(\]]([a-zA-Z+&,']+\s)*#\d+\.?\d*[)\]]"
        series = re.search(find_series_regex, full_title)
        if series:
            # if it's a series, get the series name and fix the book title
            full_title = full_title.replace(series.group(0), '')
            series = series.group(0).strip(" ()")
        book_dict['title'] = full_title
        book_dict['series'] = series
        book_dict['book_url'] = a_link.get('href')

        # parse author and author_url
        td = tr.find_all('td', {'class': 'field author'})[0]
        a_link = td.find_all('a')[0]
        last_comma_first = a_link.text

        if last_comma_first == 'NOT A BOOK':
            continue

        # capture the last name and first name
        name_regex = re.search("(.*),\s(.*)", last_comma_first)
        author_full_name = name_regex.group(2) + " " + name_regex.group(1)
        book_dict['author_name'] = author_full_name
        book_dict['author_url'] = a_link.get('href')

        # parse rating
        td = tr.find_all('td', {'class': 'field rating'})[0]
        span = td.find_all('span', {'class': 'staticStars notranslate'})[0]
        rating_text = span.get('title')
        rating = get_rating_from_text(rating_text)
        book_dict['rating'] = rating

        # parse review
        review = ''
        td = tr.find_all('td', {'class': 'field review'})
        if(len(td) > 0):
            td = td[0]
            span = td.find_all('span')
            if(len(span) > 0):
                span = span[-1]
                lines = [str(i) for i in span.contents]
                review = ' '.join(lines)
        book_dict['review'] = review

        # parse date_started
        td = tr.find_all('td', {'class': 'field date_started'})[0]
        span = td.find_all('span', {'class': 'date_started_value'})
        dates_started = []
        for date_html in span:
            date_started = date_html.text
            dates_started.append(convert_date_to_isoformat(date_started))
        book_dict['date_started'] = max(dates_started)
        # store number of dates started to confirm # of dates finished
        reads = len(dates_started)

        # parse date_read
        td = tr.find_all('td', {'class': 'field date_read'})[0]
        dates_finished = []
        try:
            span = td.find_all('span', {'class': 'date_read_value'})
            for date_html in span:
                date_read = date_html.text
                dates_finished.append(convert_date_to_isoformat(date_read))
        except IndexError:
            dates_finished = []  # no date finished

        if len(dates_finished) < reads:
            book_dict['date_read'] = None  # not finished
        else:
            book_dict['date_read'] = max(dates_finished)

        book_list.append(book_dict)

    return book_list


def get_book_details_from_url(book_url):
    """Get the book details from the url provided."""
    # scrape the url for the html
    html_str = get_html_using_selenium(book_url)

    # parse the html string for the book details
    soup = BeautifulSoup(html_str, 'lxml')

    publication_html = soup.find_all(
        'div',
        {'id': 'details'}
    )[0].find_all('div', {'class': 'row'})[1]
    publication_date = re.search(r'Published\s+(.*)\s+', publication_html.text.strip()).group(1)

    genres_list_html = soup.find_all('a', {'class': 'actionLinkLite bookPageGenreLink'})
    genres = [genre.text for genre in genres_list_html]
    genres = set(genres)  # use set to remove duplicates
    if "Audiobook" in genres:
        genres.remove("Audiobook")

    numberOfPages_html = soup.find_all('span', {'itemprop': 'numberOfPages'})[0]
    page_count = re.search(r'\d+', numberOfPages_html.text).group()
    page_count = int(page_count)

    book_details = {
        'publication_date': publication_date,
        'genres': list(genres),
        'page_count': page_count,
    }
    return book_details


def filter_and_sort_books(book_list, year):
    filtered_list = [i for i in book_list if year in i['date_read']]
    sorted_list = sorted(filtered_list, key=lambda k: k['date_read'], reverse=True)
    return sorted_list


def get_read_and_reading(urls=[URL_BOOKS_READ, URL_CURRENTLY_READING]):
    book_lists = []

    for url in urls:
        # get the webpage html
        html_str = get_html_using_selenium(url)
        # get the book data list (reading or read)
        book_list = get_books_list_data_from_html(html_str)
        book_lists.append(book_list)

        # save_json_to_file(book_list, f'./json/books_{url[76:80]}.json')

    return book_lists


# get books read
# html = get_html_using_selenium(URL_BOOKS_READ)
# write_to_file(html, './json/goodreads_html.html')
# books_read = get_books_list_data_from_html(html)


# books_read, currently_reading = get_read_and_reading(
#     [URL_BOOKS_READ, URL_CURRENTLY_READING]
# )

# save_json_to_file(books_read, './json/books_read.json')
# save_json_to_file(currently_reading, './json/books_currently_reading.json')


def convert_date_to_isoformat(date_str):
    if date_str is None:
        return None

    date_str = date_str.strip()
    try:
        date_obj = datetime.datetime.strptime(date_str, '%b %d, %Y')
    except ValueError:
        date_obj = datetime.datetime.strptime(date_str, '%b %Y')

    return date_obj.strftime('%Y-%m-%d')
