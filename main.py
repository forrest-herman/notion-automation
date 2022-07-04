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

templatePage_id = read_database_pages(database_id_journal, headers)
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
    "children": templateBlocks
}

newPage_id = create_page(headers, newPageData_journal)["id"]


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
