import os

from notion_daily_journal import generate_journal_entry
from notion_api_methods import *
import notion_reading_list_update
import goodreads

# load environment variables
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('NOTION_TOKEN')  # notion credentials


# Goodreads work here
books_read, currently_reading = goodreads.get_read_and_reading()
notion_reading_list_update.update_reading_list(books_read, currently_reading)

# create a new journal page daily
generate_journal_entry()
