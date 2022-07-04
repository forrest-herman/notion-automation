# api_methods.py

import requests
from datetime import datetime

from utils import save_json_to_file


def readDatabase(database_id_journal, headers):
    url = f'https://api.notion.com/v1/databases/{database_id_journal}'
    result = requests.get(url, headers=headers)
    print(result.status_code)

    data = result.json()

    # save_json_to_file(data, './json/db_data.json')

    return data


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
    """ Append child blocks to a page or block """
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'

    print(blocks_data)
    payload = {
        "children": blocks_data
    }

    res = requests.patch(url, headers=headers, json=payload)
    print(res.status_code)

    data = res.json()
    # print(data)

    # save_json_to_file(data, './json/page_data.json')

    return data


def create_page(headers, newPageData):
    """ Create a new page in the provided database """
    url = 'https://api.notion.com/v1/pages'

    res = requests.post(url, headers=headers, json=newPageData)
    print(res.status_code)
    save_json_to_file(res.json(), './json/new_page_data.json')

    return res.json()
