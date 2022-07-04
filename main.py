from datetime import datetime
# import requests

import config
from api_methods import *

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

# print(datetime.now().isoformat())
today = datetime.now().date().isoformat()

# get the correct template based on weekday or weekend
if datetime.now().weekday() < 5:
    pageName = "Daily Summary Preteckt Template"
else:
    pageName = "Daily Summary Template"

template_query_payload = {
    "page_size": 10,
    "filter": {
        "property": "Name",
        "rich_text": {
            "equals": pageName
        }
    }
}

today_query_payload = {
    "page_size": 10,
    "filter": {
        "property": "Date",
        "date": {
            "equals": today
        }
    }
}

# check if page already exists
exists = query_database_pages(database_id_journal, headers, today_query_payload)

if exists:
    print("Page already exists")
    exit()

templatePage_id = query_database_pages(
    database_id_journal, headers, template_query_payload)[0]['id']
templateBlocks = read_block_children(templatePage_id, headers)

newPageData_journal = {
    "parent": {"database_id": database_id_journal},
    "properties": {
        "Name": {
            "title": [
                {
                    "type": "mention",
                    "mention": {
                        "type": "date",
                        "date": {
                            "start": today,
                        }
                    }
                }
            ]
        },
        "Date": {
            "date": {
                "start": today,
            }
        },
    },
    "children": templateBlocks
}

# create the new page
newPage_id = create_page(headers, newPageData_journal)["id"]

# read the new pages blocks (so we can append their children)
newBlocks = read_block_children(newPage_id, headers)

# check for children and append those!
i = 0
for block in templateBlocks:
    if block["has_children"]:
        append_block_children(
            newBlocks[i]["id"],
            headers,
            read_block_children(block["id"], headers)
        )
    i += 1
