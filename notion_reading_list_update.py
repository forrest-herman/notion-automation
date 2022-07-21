from notion_api_methods import *
import notion_utils

reading_database_id = '252dcf91b52847888bf3d49357af4a7b'


def update_reading_list(read_list, currently_reading_list):
    """
    Take in list of books read and currently reading from Goodreads
    and update the reading list in Notion.
    """

    # check Notion for currently reading
    query_payload = {
        "filter": {
            "property": "Date started",
            "date": {
                "after": "2020-01-10"
            }
        }
    }
    notion_reading_list = query_database_pages(reading_database_id, query_payload)

    notion_books = {
        notion_utils.get_page_name(page, "Book Title"): {
            "author": page['properties']['Author']['select']['name'],
            "page_id": page['id'],
            "status": page["properties"]["Status"]["status"]["name"],
            "date_finished": page["properties"]["Date finished"]["date"]["start"] if page["properties"]["Date finished"]["date"] else None,
        } for page in notion_reading_list
    }

    # check all books in reading list
    for book in read_list:
        # check if book is in the reading list
        if(book['title'] in notion_books):
            # print(book['title'], 'exists already')
            notion_book = notion_books[book['title']]

            # check if the book has been finished
            if(notion_book['status'] != 'Read' or notion_book['date_finished'] is None):
                # check the author matches (in case of multiple books with same title)
                if(notion_book['author'] != book['author_name']):
                    print('Author mismatch, skipping')
                    continue
                # update the book page
                # change status to READ and update date_finished
                update_book_page(notion_book, book)
                print("Updated", book['title'], "to Read")
        else:
            # if book doesn't exist, create it
            print('create new book page', book['title'])
            create_book_page(book)

    for book in currently_reading_list:
        # create_or_update_book_page(book, notion_books)
        print('Currently Reading', book['title'])
        if(book['title'] not in notion_books):
            create_book_page(book)

    # END OF SCRIPT


def create_book_page(book_details):
    newPageData_book = {
        "parent": {"database_id": reading_database_id},
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
                                "url": "www.goodreads.com" + book_details['book_url']
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
            #         "name": "Read"  # if book_details['date_read'] else "Currently Reading",
            #     }
            # },
            "Rating": {
                "type": "select",
                "select": {
                    "name": "⭐️" * int(book_details['rating']),
                } if book_details['rating'] else None
            },
            # "Tags": {
            #     "multi_select": [
            #         {
            #             'name': tag['name']
            #         } for tag in book_details['tags']
            #     ]
            # },
        },
    }

    newPage = create_page(newPageData_book)
    return newPage


def update_book_page(page_to_update, book_details):
    # update page properites
    newBookPageData = {
        "properties": {
            "Date finished": {
                "date": {
                    "start": book_details['date_read']
                }
            },
            # "Status": {
            #     "status": {
            #         "name": "Read",
            #     }
            # },
            "Rating": {
                "type": "select",
                "select": {
                    "name": "⭐️" * int(book_details['rating']),
                } if book_details['rating'] else None
            },
        },
    }

    return update_page(page_to_update['page_id'], newBookPageData)
