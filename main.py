import os

from notion_daily_journal import generate_journal_entry
from notion_api_methods import *
import notion_reading_list_update
import goodreads
from utils import save_json_to_file

# Goodreads work here
books_read, currently_reading = goodreads.get_read_and_reading()
if len(currently_reading) == 1:
    # if there is a book currently being read
    progress = goodreads.get_progress_from_home_page()
    currently_reading[0]['progress'] = progress

    # store the current book in a json file with the progress
    save_json_to_file(currently_reading[0], 'json/current_book.json')
else:
    print("Too many books currently being read")

notion_reading_list_update.update_reading_list(books_read, currently_reading)

# create a new journal page daily
# generate_journal_entry()
