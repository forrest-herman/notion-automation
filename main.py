import requests
import json
from datetime import datetime

import config

# see instructions here https://developers.notion.com/reference/retrieve-a-database

token = config.token

database_id = '3f6b1a7d1198421f83365c74cdb7f23f'  # Journal

headers = {
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
}


def readDatabase(database_id, headers):
    url = f'https://api.notion.com/v1/databases/{database_id}'
    result = requests.get(url, headers=headers)
    print(result.status_code)

    data = result.json()

    with open('./db.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def create_page(database_id, headers):
    url = 'https://api.notion.com/v1/pages'

    newPageData = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "type": "mention",
                        "mention": {
                            "type": "date",
                            "date": {
                                "start": datetime.now().date().isoformat(),
                            }
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": datetime.now().date().isoformat(),
                }
            },
        },
        "children": [
            {
                "object": "block",
                "type": "template",
                "template": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Create callout template"
                            }
                        }
                    ],
                    "children": [
                        {
                            "callout": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Placeholder callout text"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
        ]
    }

    res = requests.post(url, json=newPageData, headers=headers)
    print(res.text)
    print(res.status_code)


print(datetime.now().isoformat())
readDatabase(database_id, headers)
create_page(database_id, headers)
