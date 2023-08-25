import datetime
import os

from notion_api_methods import *
from notion_insurance_tracker import add_new_appointment
import utils

# import cloudinary

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


# today = datetime.date.today() + datetime.timedelta(days=1)
# today = today.isoformat()
today = datetime.date.today().isoformat()
weekday = datetime.date.today().weekday()


##################################################################


def query_journal() -> tuple[dict, dict]:
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
    today_journal = query_database_pages(database_id_journal, today_query_payload)

    if not today_journal:
        return None, None
    
    # check if page has content
    content = read_block_children(today_journal[0]['id'])
    if content:
        print("Journal page already exists with content")
        return today_journal[0], content
    
    print("Blank journal page already exists")
    return today_journal[0], None


def build_template_query_payload():
    # get the correct template based on weekday or weekend
    if weekday < 5:  # monday - friday
        pageName = "Daily Summary OtO Template"
        # pageName = "Daily Summary Preteckt Template"
    else:
        pageName = "Daily Summary Template"

    # OVERWRITE 
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

    return template_query_payload


# MAIN SCRIPT

def generate_journal_entry():
    """Main script to create daily journal entry."""

    existing_journal_page, existing_journal_content = query_journal()
    # if existing_journal_page.get('content') is not None:
    #     return None
    
    template_query_payload = build_template_query_payload()

    # get the template page id and read its blocks
    templatePage_id = query_database_pages(
        database_id_journal, template_query_payload)[0]['id']
    templateBlocks = read_block_children_recursive(templatePage_id, headers)

    # get the property id of the jounral page template and read the property tags
    tag_property_id = read_database(database_id_journal, headers)['properties']['Tags']['id']
    tags_property = read_page_properties(templatePage_id, tag_property_id, headers)

    # build properties tag payload for the new page
    newPage_tags = {
        tags_property['type']: [
            {
                'name': multi_select['name']
            } for multi_select in tags_property[tags_property['type']]
        ]
    }

    ##########################################
    # add more tags to the properties of a page
    ##########################################
    tags_to_add = []

    # if weekday == 1:  # tuesday
    #     tags_to_add.append({'name': 'Groceries 🛒'})

    # get calendar details and add more content to the body of the page
    newBlocks, events_today_info = get_new_body_content_and_cal_events()

    # check if certain events match page property tags
    tags_to_add.extend(check_for_event_tags(events_today_info))

    newPage_tags[tags_property['type']].extend([{'name': tag} for tag in tags_to_add])

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

    # add all the new blocks to the template
    for count, block in enumerate(newBlocks):
        # list.insert(index, elem)
        templateBlocks.insert(1 + count, block)

    if existing_journal_page is None:
        # create the new page
        newPage_id = create_page(newPageData_journal)["id"]
    elif existing_journal_content is None:
        # blank journal page exists already
        # update page properties for the blank journal page
        newPage_id = update_page(existing_journal_page['id'], newPageData_journal)["id"]
    else:
        # ensure properties are correct
        existing_page_tags = existing_journal_page['properties']['Tags']['multi_select']
        template_tags_l = [t['name'] for t in newPage_tags['multi_select']] # list of tags in template
        for tag in existing_page_tags:
            if tag['name'] not in template_tags_l:
                newPageData_journal["properties"]["Tags"]['multi_select'].append(tag) 
        update_page(existing_journal_page['id'], newPageData_journal)["id"]
        return None # page already exists with content

    # add the template blocks to the new page (including sub_children)
    append_block_children(newPage_id, templateBlocks)

    # optional: update the page properties
    # update_journal_page_properties(newPage_id)

    return True
    ##########################################
    # END OF MAIN SCRIPT
    ##########################################


def get_todays_events(today_start, today_end):
    # prepare file paths

    if OS_NAME:
        client_secret_location = 'credentials/gcal_client_secret.json'
        CREDENTIALS_FILE = os.path.join(
            os.path.dirname(__file__), client_secret_location)
        token_location = 'credentials/token.pickle'
        TOKEN_FILE = os.path.join(os.path.dirname(__file__), token_location)
    else:
        CREDENTIALS_FILE = 'google-credentials.json'
        # TOKEN_FILE = cloudinary.utils.cloudinary_url("token.pickle", resource_type="raw")
        TOKEN_FILE = 'token.pickle'

    try:
        # create a Google Calendar API service object
        cal = GoogleCalendarAccount(CREDENTIALS_FILE, TOKEN_FILE)

        events_from_all_calendars = cal.get_all_events(
            timeMin=today_start,
            timeMax=today_end,
            singleEvents=True,
            orderBy='startTime',
            timeZone='America/Toronto'
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
                'summary': cal_utils.get_summary_if_possible(event),
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
        return events_today_info

    except Exception as e:
        print("Error with GCal API", e)
        return []


def get_new_body_content_and_cal_events():
    # add more content to the body of the page

    # get all calendar events for the current day
    today_start, today_end = cal_utils.get_today_timerange()

    # Google Calendar API
    events_today_info = get_todays_events(today_start, today_end)
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
    return newBlocks, events_today_info


def update_journal_page_tags(newPage_id, tags):
    # Note: This replaces all tags on the page
    tag_object = {
        "Tags": {
            "type": "multi_select",
            "multi_select": [
                {
                    'name': tag
                } for tag in tags
            ]
        }
    }
    return update_journal_page_properties(newPage_id, tag_object)


def update_journal_page_properties(newPage_id, new_properties_dict):
    """ 
    "properties": {
        "Tags": {
            "type": "multi_select",
            "multi_select": [
                {
                    'name': 'Angèle 💕'
                },
            ]
        }
    },
    """
    # update page properites
    newPageData_journal = {
        "properties": new_properties_dict
    }

    return update_page(newPage_id, newPageData_journal)


def check_for_event_tags(events_today_info):
    # TODO: get list of Journal tags from Notion get_all_journal_tags()
    # TODO: Loop through and check if any of the events today match the tags using regex
    # tag_short = re.search(r'([a-Z]+)', tag.lower())
    # if tag_short in event['summary'].lower()

    # check if certain events match page property tags
    # if so, add the tag to the page
    tags = []

    for event in events_today_info:
        event_summary = event['summary'].lower()

        if 'fencing' in event_summary:
            tags.append('Fencing 🤺')
        if 'grocery' in event_summary:
            tags.append('Groceries 🛒')
        if 'angèle' in event_summary:
            tags.append('Angèle 💕')
        if 'macfe' in event_summary or 'formula' in event_summary:
            tags.append('MACFE')
        if 'wedding' in event_summary:
            tags.append('Wedding')
            tags.append('Photography 📷')
        if 'jennifer rapley' in event_summary:
            tags.append('Therapy ☯')
            # add to insurance coverage tracker
            add_new_appointment('Therapy', cost=135, emoji='☯')
        if 'dentist' in event_summary:
            tags.append('Dentist 🦷')
            # add to insurance coverage tracker
            add_new_appointment('Dentist', emoji='🦷')
        if 'physio' in event_summary:
            tags.append('Physio 🦵')
            # add to insurance coverage tracker
            add_new_appointment('Physiotherapy', emoji='🦵')
        if 'chiro' in event_summary:
            tags.append('Chiropractor')
            # add to insurance coverage tracker
            add_new_appointment('Chiropractor', emoji='💆')
        if 'massage' in event_summary:
            tags.append('Massage')
            # add to insurance coverage tracker
            add_new_appointment('Massage', emoji='💆')
        if '1-on-1' in event_summary:
            tags.append('1-on-1')

    return tags


def get_all_journal_tags():
    # get a list of all tags in the journal
    data = read_database(database_id_journal, headers)
    tag_options = data["properties"]["Tags"]["multi_select"]["options"]
    return [tag_prop.get("name", "") for tag_prop in tag_options]
