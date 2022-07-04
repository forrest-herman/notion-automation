import requests
import json
from datetime import datetime

import config

# see instructions here
# https://developers.notion.com/reference/retrieve-a-database

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

    with open('./json/db.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_database_pages(database_id, headers):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'

    # get the correct template based on weekday or weekend
    if datetime.now().weekday() < 5:
        pageName = "Daily Summary Preteckt Template"
    else:
        pageName = "Daily Summary Template"

    payload = {
        "page_size": 10,
        "filter": {
            "property": "Name",
            "rich_text": {
                "equals": pageName
            }
        }
    }

    result = requests.post(url, headers=headers, json=payload)
    print(result.status_code)

    data = result.json()

    # read_block_children(data['results'][0]['id'], headers)

    with open('./json/db_query.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data['results'][0]['id']


def read_block_children(block_id, headers):
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'
    res = requests.get(url, headers=headers)
    print(res.status_code)

    data = res.json()

    with open('./json/page_data.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data["results"]


def create_page(database_id, headers, blocks_data):
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
        "children": blocks_data
    }

    res = requests.post(url, headers=headers, json=newPageData)
    print(res.status_code)


# print(datetime.now().isoformat())

databasePage_id = read_database_pages(database_id, headers)
templateBlocks = read_block_children(databasePage_id, headers)
create_page(database_id, headers, templateBlocks)
