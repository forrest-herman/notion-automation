import os
import requests

from utils import save_json_to_file

# load environment variables
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('NOTION_TOKEN')  # notion credentials

# see instructions here
# https://developers.notion.com/reference/retrieve-a-database

HEADERS = {
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + TOKEN
}


def read_database(database_id, headers=HEADERS):
    url = f'https://api.notion.com/v1/databases/{database_id}'
    result = requests.get(url, headers=headers)
    if (result.status_code != 200):
        print(result.status_code)

    data = result.json()

    # save_json_to_file(data, './json/db_data.json')

    return data


def query_database_pages(database_id, query_payload, headers=HEADERS):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'

    result = requests.post(url, headers=headers, json=query_payload)
    if (result.status_code != 200):
        print(result.status_code)
        print("query_database_pages:", result.text)

    data = result.json()

    # save_json_to_file(data['results'], './json/db_query.json')

    return data['results']


def read_page_properties(page_id, property_id, headers=HEADERS):
    """
    Read page properties.
    To obtain property_id's, use the read_database endpoint.
    """
    url = f'https://api.notion.com/v1/pages/{page_id}/properties/{property_id}'
    res = requests.get(url, headers=headers)
    if (res.status_code != 200):
        print(res.status_code)

    data = res.json()

    # save_json_to_file(data, './json/page_properties.json')

    return data


# DELETE THIS?
def read_block_children(block_id, headers=HEADERS):
    """ Read child blocks of a page or block """
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'
    res = requests.get(url, headers=headers)
    if (res.status_code != 200):
        print(res.status_code)

    data = res.json()

    # save_json_to_file(data["results"], './json/page_data.json')

    return data["results"]


def read_block_children_recursive(block_id, headers=HEADERS):
    """ Read child blocks of a page or block and their children, etc. """
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'
    res = requests.get(url, headers=headers)
    if (res.status_code != 200):
        print(res.status_code)
        print("read_block_children_recursive", res.text)

    data = res.json()

    for block in data["results"]:
        if (block["has_children"]):
            block[block["type"]]["children"] = read_block_children_recursive(block["id"], headers)

    # save_json_to_file(data["results"], './json/block_children.json')

    return data["results"]


def append_block_children(block_id, blocks_data, headers=HEADERS):
    """ Append child blocks to a page or block """
    url = f'https://api.notion.com/v1/blocks/{block_id}/children'

    payload = {
        "children": blocks_data
    }

    res = requests.patch(url, headers=headers, json=payload)
    if (res.status_code != 200):
        print(res.status_code)
        print("append_block_children", res.text)

    data = res.json()

    # save_json_to_file(payload, './json/new_page_children_data.json')

    return data


def create_page(newPageData, headers=HEADERS):
    """ Create a new page in the provided database """
    url = 'https://api.notion.com/v1/pages'

    res = requests.post(url, headers=headers, json=newPageData)
    if (res.status_code != 200):
        print(res.status_code)
        print("create_page", res.text)
        exit()

    # save_json_to_file(res.json(), './json/new_page_data.json')

    return res.json()


def update_page(page_id, payload, headers=HEADERS):
    """
    This endpoint is for updating page properties, not page content.
    To fetch page content, use the retrieve block children endpoint.
    To append page content, use the append block children endpoint.

    payload = {
        "properties": "gfdg",
        "archived": False,
        "icon": "gdsfg",
        "cover": "dsgdg"
    }
    """
    url = f'https://api.notion.com/v1/pages/{page_id}'

    res = requests.patch(url, headers=headers, json=payload)
    if (res.status_code != 200):
        print(res.status_code)
        print("update_page", res.text)
        exit()

    # save_json_to_file(res.json(), './json/new_page_data.json')

    return res.json()
