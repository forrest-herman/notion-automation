import requests
from datetime import datetime

import config
from utils import save_json_to_file

# see instructions here
# https://developers.notion.com/reference/retrieve-a-database

token = config.token

database_id_journal = '3f6b1a7d1198421f83365c74cdb7f23f'  # Journal

headers = {
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
}


def readDatabase(database_id_journal, headers):
    url = f'https://api.notion.com/v1/databases/{database_id_journal}'
    result = requests.get(url, headers=headers)
    print(result.status_code)

    data = result.json()

    # save_json_to_file(data, './json/db_data.json')


def read_database_pages(database_id_journal, headers):
    url = f'https://api.notion.com/v1/databases/{database_id_journal}/query'

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

    # save_json_to_file(data, './json/db_query.json')

    return data['results'][0]['id']


def read_block_children(block_id, headers):
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'
    res = requests.get(url, headers=headers)
    print(res.status_code)

    data = res.json()

    # save_json_to_file(data["results"], './json/page_data.json')

    return data["results"]


def append_block_children(block_id, headers, blocks_data):
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'

    print(blocks_data)
    payload = {
        "children": blocks_data
    }

    res = requests.patch(url, headers=headers, json=payload)
    print(res.status_code)

    # data = res.json()
    # print(data)

    # save_json_to_file(data, './json/page_data.json')

    # return data["results"]


def create_page(database_id_journal, headers, blocks_data):
    url = 'https://api.notion.com/v1/pages'

    newPageData = {
        "parent": {"database_id_journal": database_id_journal},
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

    return res.json()


# print(datetime.now().isoformat())

templatePage_id = read_database_pages(database_id_journal, headers)
templateBlocks = read_block_children(templatePage_id, headers)
newPage_id = create_page(database_id_journal, headers, templateBlocks)["id"]


i = 0
newBlocks = read_block_children(newPage_id, headers)

# check for children and append those!
for block in templateBlocks:
    if block["has_children"]:
        append_block_children(
            newBlocks[i]["id"],
            headers,
            read_block_children(block["id"], headers)
        )
    i += 1
