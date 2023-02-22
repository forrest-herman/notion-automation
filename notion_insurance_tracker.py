import datetime
from notion_api_methods import *

database_id_insurance = '7f213122bd5d41db995bb770c0d130c1'


def add_new_appointment(type, cost, date=None):
    """Add a new appointment to the database"""

    if date is None:
        date = datetime.date.today()

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
            }
        },
        "icon": {
            "type": "emoji",
            "emoji": "☯"
        }
    }

    create_page(new_appointment_data)
