import datetime
import os

from notion_api_methods import *
import utils

# custom package found at:
# https://github.com/forrest-herman/python-packages-common/tree/main/google_calendar_integrations
from google_calendar_integrations.gcal_methods import GoogleCalendarAccount
from google_calendar_integrations import cal_utils
# use this command to pull the latest changes:
# pip install -e "git+https://github.com/forrest-herman/python-packages-common.git@main#egg=google_calendar_integrations&subdirectory=google_calendar_integrations"

# load environment variables
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('NOTION_TOKEN')  # notion credentials
OS_NAME = os.getenv('OS')

# see instructions here
# https://developers.notion.com/reference/retrieve-a-database

database_id_journal = '3f6b1a7d1198421f83365c74cdb7f23f'  # Journal

headers = {
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + TOKEN
}


# print(datetime.datetime.now().isoformat())
today = datetime.date.today().isoformat()
weekday = datetime.date.today().weekday()


##################################################################


def build_template_query_payload():
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
    exists = query_database_pages(database_id_journal, today_query_payload)

    if exists:
        print("Page already exists")
        # today = datetime.date.today() + datetime.timedelta(days=1)
        # today = today.isoformat()
        exit()

    return template_query_payload


# MAIN SCRIPT

def generate_journal_entry():
    """Main script to create daily journal entry."""

    template_query_payload = build_template_query_payload()

    # get the template page id and read it's blocks
    templatePage_id = query_database_pages(
        database_id_journal, template_query_payload)[0]['id']
    templateBlocks = read_block_children_recursive(templatePage_id, headers)

    # get the property id of the jounral page template and read the property tags
    properties_id = read_database(database_id_journal, headers)['properties']['Tags']['id']
    properties = read_page_properties(templatePage_id, properties_id, headers)

    # build properties tag payload for the new page
    newPage_tags = {
        properties['type']: [
            {
                'name': multi_select['name']
            } for multi_select in properties[properties['type']]
        ]
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

    # add more content to the body of the page
    newBlocks = get_new_body_content()

    # add all the new blocks to the template
    for count, block in enumerate(newBlocks):
        # list.insert(index, elem)
        templateBlocks.insert(1 + count, block)

    # create the new page
    newPage_id = create_page(newPageData_journal)["id"]

    # add the template blocks to the new page (including sub_children)
    append_block_children(newPage_id, templateBlocks)

    # optional: update the page properties
    # update_journal_page_properties(newPage_id)

    ##########################################
    # END OF MAIN SCRIPT
    ##########################################


def get_new_body_content():
    # add more content to the body of the page

    # get all calendar events for the current day
    today_start, today_end = cal_utils.get_today_timerange()

    # Google Calendar API

    # prepare file paths
    client_secret_location = 'credentials/gcal_client_secret.json'
    CREDENTIALS_FILE = os.path.join(
        os.path.dirname(__file__), client_secret_location)
    token_location = 'credentials/token.pickle'
    TOKEN_FILE = os.path.join(os.path.dirname(__file__), token_location)

    try:
        # create a Google Calendar API service object
        cal = GoogleCalendarAccount(CREDENTIALS_FILE, TOKEN_FILE)

        events_from_all_calendars = cal.get_all_events(
            timeMin=today_start,
            timeMax=today_end,
            singleEvents=True,
            orderBy='startTime'
        )
        """ 
        Example:

        result = gcal_methods.get_calendar_events(
            calendarId='primary',
            maxResults=10,
            timeMin=today_start,
            timeMax=today_end,
            singleEvents=True,
            orderBy='startTime'
        )
        """

        events_today_info = [
            {
                'summary': event['summary'],
                'calendar': event['calendar'],
                'htmlLink': event['htmlLink'],
                'start': cal_utils.get_datetime_from_event(event['start']),
                # basically: event['end']['dateTime'] or event['end']['date']
                'end': cal_utils.get_datetime_from_event(event['end'])
            } for event in events_from_all_calendars]

        # events_today = set(events_today)  # remove duplicates
        # filter events
        events_today_info = cal_utils.filter_events_by_calendar(
            events_today_info, ['Personal old', 'angele.beaulne@gmail.com'],
            exclude=True
        )

    except Exception as e:
        print("Error with GCal API", e)

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
                            "content": f"{event['summary']}",
                            "link": None,
                        },
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "gray"
                        },
                    },
                    {
                        "type": "text",
                        "text": {
                            "content": " ({} - {})".format(
                                event['start'].strftime(utils.get_12hr_time_format_for_os(OS_NAME)),
                                event['end'].strftime(utils.get_12hr_time_format_for_os(OS_NAME))
                            ) if not cal_utils.is_all_day(event) else " (all day)",
                            "link": {
                                'type': 'url',
                                'url': event['htmlLink']
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
    return newBlocks


def update_journal_page_properties(newPage_id):
    # update page properites
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

    return update_page(newPage_id, newPageData_journal)
