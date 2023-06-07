import datetime
from notion_api_methods import *

database_id_insurance = '7f213122bd5d41db995bb770c0d130c1'
database_id_pivot = '8242f0300dda4be398b210b1e92285ab'


def query_insurance_database(date) -> bool:
    payload = {
        "page_size": 10,
        "filter": {
            "property": "Date",
            "date": {
                "equals": date.isoformat()
            }
        }
    }

    # check if page already exists
    today_journal = query_database_pages(database_id_insurance, payload)

    if not today_journal:
        return False
    return True


def get_latest_pivot_table_year(date) -> str:
    date = date.isoformat()
    year = date[:4]

    # TODO: fix this query for the date is between start and end
    payload = {
        "filter": {
            "property": "Timeframe",
            "date": {
                "past_year": {}
            }
            # "and": [
            #     {
            #         "property": "Timeframe",
            #         "date": {
            #             "before": date
            #         }
            #     },
            #     {
            #         "property": "Timeframe",
            #         "date": {
            #             "after": date
            #         }
            #     }
            # ]
        }
    }
    pivot_pages = query_database_pages(database_id_pivot, payload)
    if len(pivot_pages) == 0:
        # create new stats page for the year
        newPageData = {
            "parent": {"database_id": database_id_pivot},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": f'{year}-{int(year) + 1}'
                            }
                        }
                    ]
                },
                "Timeframe": {
                    "date": {
                        "start": datetime.date(int(year), 9, 1).isoformat(),
                        "end": datetime.date(int(year) + 1, 8, 31).isoformat() # double check
                    }
                }
            }
        }
        pivot_page_id = create_page(newPageData)["id"]
    else:
        pivot_page_id = pivot_pages[0]['id']

    return pivot_page_id


def add_new_appointment(type, cost, date=None):
    """Add a new appointment to the database"""

    if date is None:
        date = datetime.date.today()

    # check if page already exists
    if query_insurance_database(date):
        print(f"Appointment already exists for {date.isoformat()}")
        # return

    new_appointment_data = {
        "parent": {"database_id": database_id_insurance},
        "properties": {
            "": {
                "title": [
                    {
                        "type": "mention",
                        "mention": {
                            "type": "date",
                            "date": {
                                "start": date.isoformat(),
                            }
                        }
                    }
                ]
            },
            "Type": {
                "type": "select",
                "select": {
                    "name": type
                }
            },
            "Cost": {
                "number": cost
            },
            "Date": {
                "date": {
                    "start": date.isoformat()
                }
            },
            "Linked to Pivot Table": {
                "relation": [
                    {
                        "id": get_latest_pivot_table_year(date)
                    }
                ]
            }
        },
        "icon": {
            "type": "emoji",
            "emoji": "☯"
        }
    }

    create_page(new_appointment_data)
