import datetime
from notion_api_methods import *
from tracking_games.steam_api_methods import *
# get_recently_played_games, get_game_img_url, STEAM_ID


database_id_games = 'ab34a11b1156466bb028ced90af23f96'

# helpers functions


def format_playtime_hrs(playtime_mins):
    return round(playtime_mins / 60, 1)


def get_achievement_percentage(achievements):
    total = len(achievements)
    count = sum(a['achieved'] == 1 for a in achievements)
    # for achievement in achievements:
    #     if achievement['achieved'] == 1:
    #         count += 1
    return round((count / total) * 100, 1)


# main function
def update_games_list():
    recent_games = get_recently_played_games(STEAM_ID).get('games', [])
    print(recent_games)

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    two_weeks_ago = today - datetime.timedelta(days=14)

    for game in recent_games:

        # find the game in notion if it already exists
        query_game_page_payload = {
            "page_size": 1,
            "filter": {
                "property": "Title",
                "title": {
                    "equals": game['name']
                }
            }
        }

        results = query_database_pages(database_id_games, query_game_page_payload)
        game_page = results[0] if len(results) > 0 else None

        if game_page is None:
            # game page doesn't exist, create it
            new_game_pageData = {
                "parent": {"database_id": database_id_games},
                "icon": {
                    "type": "external",
                    "external": {
                        "url": get_game_img_url(game['appid'], game['img_icon_url'])
                    }
                },
                "cover": {
                    "type": "external",
                    "external": {
                        "url": get_game_img_url(game['appid'], game['img_icon_url'])
                    }
                },
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "type": "text",
                                "text": {
                                    "content": game['name']
                                }
                            }
                        ]
                    },
                    "Dates Played": {
                        "date": {
                            "start": yesterday.isoformat(),
                        }
                    },
                    "Game Store": {
                        "type": "select",
                        "select": {
                            "name": "Steam"
                        }
                    },
                    "Hours Played": {
                        "type": "number",
                        "number": format_playtime_hrs(game['playtime_forever'])
                    },
                    "Status": {
                        "type": "status",
                        "status": {
                            "name": "In progress"
                        }
                    },
                    "appid": {
                        "type": "rich_text",
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": str(game['appid'])
                                }
                            }
                        ]
                    }
                }
            }

            print("Create new page for game:", game['name'])
            newPage_id = create_page(new_game_pageData)["id"]

        else:
            # check if playtime_forever is greater than 'hours played' column
            # TODO
            prev_hours = game_page.get('properties')['Hours Played']['number']
            if prev_hours == format_playtime_hrs(game['playtime_forever']):
                print("No change in playtime for", game['name'])
                continue

            achievements = get_user_achievements_for_game(STEAM_ID, game['appid'])
            achievements = achievements['playerstats'].get('achievements', None)

            # update last played to 2 weeks ago, unless there is no date started...
            # or that date is less than the start date

            newPageData = {
                "properties": {
                    "Dates Played": {
                        "date": {
                            "start": game_page.get('properties')['Dates Played']['date']['start'],
                            "end": yesterday.isoformat()
                        }
                    },
                    "Hours Played": {
                        "number": format_playtime_hrs(game['playtime_forever'])
                    },
                    "Status": {
                        "type": "status",
                        "status": {
                            "name": "In progress"
                        }
                    },
                    "Progress": {
                        "type": "number",
                        "number": get_achievement_percentage(achievements) if achievements is not None else None
                    }
                }
            }

            update_page(game_page["id"], newPageData)

    # TODO: any games not updated should be set to 'Taking a break'

    return True
    # The End #


# update_games_list()

# testing
# data = get_owned_games(STEAM_ID)
# game_ids = [game.get("appid") for game in data['response']['games']]
# print(game_ids)

# print(get_player_summaries(STEAM_ID))
# for id in game_ids:
#     res = get_user_achievements_for_game(STEAM_ID, id)
#     achievements = res['playerstats'].get('achievements', None)
#     if achievements is not None:
#         percent = get_achievement_percentage(achievements)
#         print(id, percent, "%")
    # get_user_stats_for_game(STEAM_ID, id)
    # break
