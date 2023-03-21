from json import JSONDecodeError
import os

from notion_daily_journal import generate_journal_entry
from track_games_methods import update_games_list
import notion_reading_list_update
import goodreads
from utils import save_json_to_file, read_json_from_file


def main():
    # create a new journal page daily
    if generate_journal_entry():
        print("Journal entry created")

    # Goodreads work here
    books_read, currently_reading = goodreads.get_read_and_reading()
    if len(currently_reading) == 0:
        try:
            # TODO: make this cloud enabled
            prev_book_details = read_json_from_file('user_data/current_book.json')
        except JSONDecodeError:
            prev_book_details = None
        if prev_book_details is not None:
            prev_book_details['progress'] = 100
            save_json_to_file(prev_book_details, 'user_data/current_book.json')
    elif len(currently_reading) == 1:
        # if there is a book currently being read
        progress = goodreads.get_progress_from_home_page()
        currently_reading[0]['progress'] = progress

        # store the current book in a json file with the progress
        save_json_to_file(currently_reading[0], 'user_data/current_book.json')
    else:
        print("Too many books currently being read")

    notion_reading_list_update.update_reading_list(books_read, currently_reading)

    update_games_list()

    # TODO: add commuting fares
    # TODO: add subscription payments


if __name__ == '__main__':
    main()
