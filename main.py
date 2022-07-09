import datetime
# import json

import config
from api_methods import *

# from utils import save_json_to_file

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

# print(datetime.datetime.now().isoformat())
# today = datetime.datetime.now().date().isoformat()
today = datetime.date.today().isoformat()
weekday = datetime.date.today().weekday()

# get the correct template based on weekday or weekend
if weekday < 5:  # monday - friday
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
    # today = datetime.date.today() + datetime.timedelta(days=1)
    # today = today.isoformat()
    exit()

templatePage_id = query_database_pages(
    database_id_journal, headers, template_query_payload)[0]['id']
templateBlocks = read_block_children_recursive(templatePage_id, headers)

# get the property id of the jounral page template
properties_id = read_database(database_id_journal, headers)['properties']['Tags']['id']

# get the tags from the template
properties = read_page_properties(templatePage_id, properties_id, headers)

# properties payload for the new page
newPage_tags = {
    properties['type']: [{'name': multi_select['name']}
                         for multi_select in properties[properties['type']]]
}

# add more tags
if weekday == 1:  # tuesday
    newPage_tags[properties['type']].append({'name': 'Groceries 🛒'})

# payload for new journal page based on template, current date and tags
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
        "Tags": newPage_tags,
    },
    # "children": templateBlocks
}

# create the new page
newPage_id = create_page(headers, newPageData_journal)["id"]

# add the template blocks to the new page (including sub_children)
append_block_children(newPage_id, headers, templateBlocks)


# ------- further implementations -------

# append the tags to the new page ???? no need
# update_page()  # ----------------------------------------------- WIP
# add tag depending on day of week etc.
# add calendar events

# if tuesday add Grocery Tag
