from notion_api_methods import *
import notion_utils
from goodreads import get_book_details_from_url

from utils import save_json_to_file

books_database_id = '252dcf91b52847888bf3d49357af4a7b'
reads_database_id = '68d90801b2cd40e0a6a7a59616d073da'
book_stats_id = '74b48b15ed1d468bb07e20adc555d01c'


def update_reading_list(read_list, currently_reading_list):
    """
    Take in list of books read and currently reading from Goodreads
    and update the library and reading list in Notion.
    """

    # check Notion for currently reading
    query_payload = {
        "filter": {
            "property": "Book Title",
            "rich_text": {
                "is_not_empty": True
            }
        },
        # "sorts": [
        #     {
        #         "property": "Date started",
        #         "direction": "descending"
        #     }
        # ]
    }
    notion_books_list = query_database_pages(books_database_id, query_payload)

    # the following needs to be changed
    # ONCE WE HAVE MORE THAN 100 BOOKS!!!!!!!
    # IDEA: Custom payload with book title for the query!
    # also check author!
    notion_books = {
        notion_utils.get_page_name(page, "Book Title"): {
            "author": page['properties']['Author']['select']['name'],
            "id": page['id'],
            "status": page["properties"]["Status"]["status"]["name"],
            "date_finished": page["properties"]["Date finished"]["date"]["start"] if page["properties"]["Date finished"]["date"] else None,
        } for page in notion_books_list
    }

    # READ LIST
    # check all books in reading list
    for goodreads_book in read_list:
        # check if book is already in notion:
        # query the books database
        notion_book = query_book_list(goodreads_book)
        if notion_book:
            # book exists in the books database already

            # logic for checking if book is in the reads database
            read_page = query_reads_list(notion_book, goodreads_book)
            if read_page is not None:
                # Book exists already on the reads list
                # check if it has a finish date
                if read_page["properties"]["Date finished"].get("date", None) is None:
                    update_read_date(read_page["id"], goodreads_book)
                    print("Date finished updated:", goodreads_book['title'])
            else:
                # book needs to be added to the reads list
                add_read_date(notion_book["id"], goodreads_book)
                print("Book added to the reads list")

            # check if the book status is correct
            if(notion_book['properties']['Status']['status']['name'] != 'Read'):
                # update the book page
                update_book_page(notion_book, goodreads_book)
                print("Updated", goodreads_book['title'], "to Read")
        else:
            # if book doesn't exist, create it
            notion_book = create_book_page(goodreads_book)
            print('Created new book page:', goodreads_book['title'])
            add_read_date(notion_book["id"], goodreads_book)

    # CURENTLY READING LIST
    for goodreads_book in currently_reading_list:
        print('Currently Reading:', goodreads_book['title'])

        # check if book is already in notion:
        notion_book = query_book_list(goodreads_book)

        if notion_book is None:
            # create the book page
            notion_book = create_book_page(goodreads_book)
            print('Created new book page', goodreads_book['title'])
            add_read_date(notion_book["id"], goodreads_book)
        else:
            # The book exists already in the Notion books database
            update_book_page(notion_book, goodreads_book)

            # check if the book has already been added to the reads list
            read_page = query_reads_list(notion_book, goodreads_book)
            if read_page is None:
                # book needs to be added to the reads list
                add_read_date(notion_book["id"], goodreads_book)
                print('Added', goodreads_book['title'], 'to the reads list')

    # END OF SCRIPT


# Helper functions
# def create_or_update_book_page(book, notion_books)


# BOOKS DATABASE

def create_book_page(book_details):
    goodreads_book_url = "https://www.goodreads.com" + book_details['book_url']
    try:
        additional_book_details = get_book_details_from_url(goodreads_book_url)
        book_details.update(additional_book_details)
    except Exception as e:
        print(e)
        # sometimes it fails for no reason, so we just retry
        additional_book_details = get_book_details_from_url(goodreads_book_url)
        book_details.update(additional_book_details)
    except:
        print('Error getting book details')

    newPageData_book = {
        "parent": {"database_id": books_database_id},
        "icon": {
            "type": "external",
            "external": {
                "url": book_details['cover_url']
            }
        },
        "properties": {
            "Book Title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": book_details['title'],
                            "link": {
                                "type": "url",
                                "url": goodreads_book_url
                            }
                        }
                    }
                ]
            },
            "Series": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": book_details['series'] if book_details['series'] else '',
                            "link": None
                        }
                    }
                ]
            },
            "Author": {
                "type": "select",
                "select": {
                    "name": book_details['author_name'],
                    # "color": "default"
                }
            },
            "Date started": {
                "date": {
                    "start": book_details['date_started'],
                }
            },
            "Date finished": {
                "date": {
                    "start": book_details['date_read']
                } if book_details['date_read'] else None
            },
            # "Status": {
            #     "type": "status",
            #     "status": {
            #         "name": "Read" if book_details['date_read'] else "Currently Reading",
            #     }
            # },
            "Rating": {
                "type": "select",
                "select": {
                    "name": "⭐️" * int(book_details['rating']),
                } if book_details['rating'] else None
            },
            "Publication Date": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": book_details.get('publication_date', ''),
                        }
                    }
                ]
            },
            "Tags": {
                "multi_select": [
                    {
                        'name': tag
                    } for tag in book_details.get('genres', [])
                ]
            },
            "Pages": {
                "number": book_details['page_count'] if type(book_details.get("page_count", "")) == int else None
            }
        },
    }
    newPage = create_page(newPageData_book)
    return newPage


def update_book_page(page_to_update, book_details):
    # update page properites
    newBookPageData = {
        "properties": {
            "Date started": {
                "date": {
                    "start": book_details['date_started']
                }
            },
            "Date finished": {
                "date": {
                    "start": book_details['date_read']
                } if book_details['date_read'] else None
            },
            # "Status": {
            #     "status": {
            #         "name": "Read" if book_details['date_read'] else "Currently Reading",
            #     }
            # },
            "Rating": {
                "type": "select",
                "select": {
                    "name": "⭐️" * int(book_details['rating']),
                } if book_details['rating'] else None
            },
            "Series": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": book_details['series'] if book_details['series'] else '',
                        }
                    }
                ]
            },
        },
    }
    return update_page(page_to_update["id"], newBookPageData)


# READS DATABASE

def add_read_date(notion_book_page_id, book_details):
    """Add a read date for a book"""
    newPageData_read = {
        "parent": {"database_id": reads_database_id},
        "properties": {
            "Date": {
                "title": [
                    {
                        "type": "mention",
                        "mention": {
                            "type": "date",
                            "date": {
                                "start": book_details['date_started'],
                            }
                        }
                    }
                ]
            },
            "Book": {
                "relation": [
                    {
                        "id": notion_book_page_id
                    }
                ]
            },
            "Date started": {
                "date": {
                    "start": book_details['date_started'],
                }
            },
            "Date finished": {
                "date": {
                    "start": book_details['date_read']
                } if book_details['date_read'] else None
            },
            # Temp: make sure it's included in stats
            "Stats": {
                "relation": [
                    {
                        "id": book_stats_id
                    }
                ]
            }
        },
    }

    newPage = create_page(newPageData_read)
    return newPage


def update_read_date(page_to_update_id, book_details):
    # update page details
    updatePageData = {
        "properties": {
            "Date started": {
                "date": {
                    "start": book_details['date_started']
                }
            },
            "Date finished": {
                "date": {
                    "start": book_details['date_read']
                }
            },
        },
    }
    return update_page(page_to_update_id, updatePageData)


# QUERY FOR NOTION DATABASE ENTRIES

def query_reads_list(notion_book, book_details):
    read_list_query_payload = {
        "filter": {
            "and": [
                {
                    "property": "Book",
                    "relation": {
                        "contains": notion_book["id"]
                    }
                },
                {
                    "property": "Date started",
                    "date": {
                        "equals": book_details["date_started"]
                    }
                }
            ]
        },
    }
    result = query_database_pages(reads_database_id, read_list_query_payload)
    if len(result) > 0:
        save_json_to_file(result[0], f"json/reads/read_list_query_result{result[0]['id']}.json")
        return result[0]
    return None


def query_book_list(book_details):
    book_query_payload = {
        "filter": {
            "and": [
                {
                    "property": "Book Title",
                    "rich_text": {
                        "equals": book_details['title']
                    }
                },
                {
                    "property": "Author",
                    "select": {
                        "equals": book_details["author_name"]
                    }
                }
            ]
        }
    }
    result = query_database_pages(books_database_id, book_query_payload)
    if len(result) > 0:
        return result[0]
    return None


# -----------------------------
# TEMP FUNCTIONS TO BUILD BOOKS
# -----------------------------

def custom_update_book_pages_with_details(page_to_update, book_details):
    goodreads_book_url = "https://www.goodreads.com" + book_details['book_url']
    try:
        additional_book_details = get_book_details_from_url(goodreads_book_url)
        book_details.update(additional_book_details)
    except Exception as e:
        print(e)
        # sometimes it fails for no reason, so we just retry
        additional_book_details = get_book_details_from_url(goodreads_book_url)
        book_details.update(additional_book_details)
    except:
        print('Error getting book details')

    # update page properites
    newBookPageData = {
        "properties": {
            "Publication Date": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": book_details.get('publication_date', ''),
                        }
                    }
                ]
            },
            "Tags": {
                "multi_select": [
                    {
                        'name': tag
                    } for tag in book_details.get('genres', [])
                ]
            },
            "Pages": {
                "number": book_details['page_count'] if type(book_details.get("page_count", "")) == int else None
            }
        },
    }
    # save_json_to_file(newBookPageData, 'json/newBookPageData.json')
    return update_page(page_to_update["id"], newBookPageData)
