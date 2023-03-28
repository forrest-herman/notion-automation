from datetime import datetime
from json import JSONDecodeError
import os

from notion_daily_journal import generate_journal_entry
from track_games_methods import update_games_list
import notion_reading_list_update
import goodreads
from utils import save_json_to_file, read_json_from_file
from firestore_methods import get_firestore_document, set_last_updated, get_current_books_from_store, add_current_book_to_store


def main():
    # create a new journal page daily
    last_updated = get_firestore_document('logs/notion_journal').get('lastUpdated')
    if last_updated is None or last_updated.date() != datetime.now().date():
        if generate_journal_entry():
            print("Journal entry created")
            set_last_updated('notion_journal')

    # Goodreads/reading tracker
    last_updated = get_firestore_document('logs/notion_readingList').get('lastUpdated')
    if last_updated is None or last_updated.date() < datetime.now().date(): # TODO: change to less than 1 hour ago
        books_read, currently_reading = goodreads.get_read_and_reading(all_time=False)
        prev_curr_books = get_current_books_from_store() # dict of book dicts

        # get progress for books that are currently being read
        if len(currently_reading) > 0:
            books_progress = goodreads.get_progress_from_home_page()
        for book in currently_reading:
            progress = books_progress.get(book['title'])
            if progress:
                book['progress'] = progress
            else:
                print(f"Progress for {book['title']} not found")

            firestore_book_key = f"{book['title']}, {book['author_name']}"
            firestore_book = prev_curr_books.get(firestore_book_key, None)
            # check if the book progress has changed
            if not firestore_book or firestore_book['progress'] != book['progress']:
                add_current_book_to_store(book)
                print(f"Book {book['title']} has been updated on Firestore")
            prev_curr_books.pop(firestore_book_key, '') # remove the old book from store if it exists

        for _key, book in prev_curr_books.items():
            if book.get('progress', 0) == 100:
                continue # book has already been marked as 100% on Firestore
            book['progress'] = 100 # the book has been finished
            add_current_book_to_store(book)
            print(f"Book {book['title']} updated on Firestore to 100%")
            
        notion_reading_list_update.update_reading_list(books_read, currently_reading)
        set_last_updated('notion_readingList') # add a log that it was successfully updated

    # gaming tracker
    last_updated = get_firestore_document('logs/notion_gamingTracker').get('lastUpdated')
    if last_updated is None or last_updated.date() < datetime.now().date():
        update_games_list()
        set_last_updated('notion_gamingTracker') # add a log that it was successfully updated

    # TODO: add commuting fares
    # TODO: add subscription payments


if __name__ == '__main__':
    main()
    