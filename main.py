import datetime
import json
# import json

from credentials import config
from api_methods import *

import gcal_methods

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

##################################################################

# print(datetime.datetime.now().isoformat())
today = datetime.date.today().isoformat()
weekday = datetime.date.today().weekday()

# get the correct template based on weekday or weekend
if weekday < 5:  # monday - friday
    pageName = "Daily Summary Preteckt Template"
else:
    pageName = "Daily Summary Template"

# prepare a payload to query the database
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
    today = datetime.date.today() + datetime.timedelta(days=1)
    today = today.isoformat()
    # exit()

# get the template page id and read it's blocks
templatePage_id = query_database_pages(
    database_id_journal, headers, template_query_payload)[0]['id']
templateBlocks = read_block_children_recursive(templatePage_id, headers)

# get the property id of the jounral page template and read the property tags
properties_id = read_database(database_id_journal, headers)['properties']['Tags']['id']
properties = read_page_properties(templatePage_id, properties_id, headers)

# build properties tag payload for the new page
newPage_tags = {
    properties['type']: [{'name': multi_select['name']}
                         for multi_select in properties[properties['type']]]
}

##########################################
# add more tags to the properties of a page
##########################################
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

##########################################
# add more content to the body of the page
##########################################

# get all calendar events for the current day
today_start = datetime.datetime.now(datetime.timezone.utc).replace(
    hour=0, minute=0, second=0, microsecond=0)
today_end = today_start + datetime.timedelta(days=1)

# format the times for the API
today_start = today_start.isoformat()
today_end = today_end.isoformat()

events_from_all_calendars = gcal_methods.get_all_events(maxResults=10,
                                          timeMin=today_start, timeMax=today_end, singleEvents=True, orderBy='startTime')

# result = gcal_methods.get_calendar_events(calendarId='primary', maxResults=10,
#                                           timeMin=today_start, timeMax=today_end, singleEvents=True, orderBy='startTime')

events_today_info = [
    {
        'summary': event['summary'],
        'htmlLink': event['htmlLink'],
        'start': datetime.datetime.fromisoformat(event['start']['dateTime']),
        'end': datetime.datetime.fromisoformat(event['end']['dateTime'])
    } for event in events_from_all_calendars]

# events_today = set(events_today)  # remove duplicates

# print(json.dumps(events_today_info, indent=4))

newBlocks = [
    {
        "object": "block",
        "has_children": False,
        "archived": False,
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "{}: {} - {}".format(event['summary'], event['start'].strftime("%#I:%M %p"), event['end'].strftime("%#I:%M %p")),
                        "link": {'type': 'url', 'url': event['htmlLink']
                                 } if event['htmlLink'] else None,
                    },
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "gray"
                    },
                }
            ],
            "color": "default"
        }
    } for event in sorted(events_today_info, key=lambda x: x['start'])
]

# add all the new blocks to the template
for count, block in enumerate(newBlocks):
    # list.insert(index, elem)
    templateBlocks.insert(1 + count, block)

# create the new page
newPage_id = create_page(headers, newPageData_journal)["id"]

# add the template blocks to the new page (including sub_children)
append_block_children(newPage_id, headers, templateBlocks)


#########################
# update page properites
#########################
newPageData_journal = {
    "properties": {
        "Tags":
        {
            "type": "multi_select",
            "multi_select": [
                {
                    'name': 'Angèle 💕'
                },
            ]
        }
    },
}

# update_page(newPage_id, headers, newPageData_journal)

# ------- further implementations -------
# add calendar events
