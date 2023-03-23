from datetime import datetime
from json import JSONDecodeError
import os

from notion_daily_journal import generate_journal_entry
from track_games_methods import update_games_list
import notion_reading_list_update
import goodreads
from utils import save_json_to_file, read_json_from_file
from firestore_methods import get_firestore_document, set_last_updated, get_current_book, set_current_book


def main():
    # create a new journal page daily
    last_updated = get_firestore_document('logs', 'journal')['lastUpdated']
    if last_updated is None or last_updated.date() != datetime.now().date():
        if generate_journal_entry():
            print("Journal entry created")
            set_last_updated('journal', datetime.now())

    # Goodreads work here
    books_read, currently_reading = goodreads.get_read_and_reading()
    prev_book_details = get_current_book()
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

        # check if book data has changed
        if currently_reading[0] != prev_book_details:
            set_current_book(currently_reading[0])

        # store the current book in a json file with the progress
        save_json_to_file(currently_reading[0], 'user_data/current_book.json')
    else:
        # TODO: improve this using collection
        print("Too many books currently being read")

    notion_reading_list_update.update_reading_list(books_read, currently_reading)
    # ^ add a log that it was successfully updated

    update_games_list()
    # ^ add a log that it was successfully updated

    # TODO: add commuting fares
    # TODO: add subscription payments


if __name__ == '__main__':
    main()
