import datetime
from notion_api_methods import *
from tracking_games.steam_api_methods import *
# get_recently_played_games, get_game_img_url, STEAM_ID


database_id_games = 'ab34a11b1156466bb028ced90af23f96'

# helpers functions


def format_playtime_hrs(playtime_mins):
    return round(playtime_mins / 60, 1)


def get_achievement_percentage(achievements):
    if achievements is None:
        return None
    total = len(achievements)
    # sum all true achievements
    count = sum(a['achieved'] == 1 for a in achievements)
    return round((count / total) * 100, 1)


# main function
def update_games_list():
    recent_games = get_recently_played_games(STEAM_ID).get('games', [])

    for game in recent_games:
        print("Working on", game['name'])
        # process the game data from the api query
        extra_game_info = get_owned_games(STEAM_ID, [game['appid']])
        # TODO: for the future, track games that aren't recently played
        # but probably only do it once a week
        timestamp = extra_game_info['response']['games'][0]['rtime_last_played']

        last_played = datetime.datetime.fromtimestamp(timestamp)
        start_play = last_played - datetime.timedelta(minutes=game['playtime_forever'])

        # find the game in notion if it already exists
        query_game_page_payload = {
            "page_size": 1,
            "filter": {
                "and": [
                    {
                        "property": "Game Store",
                        "select": {
                            "equals": "Steam"
                        }
                    },
                    {
                        "or": [
                            {
                                "property": "Title",
                                "title": {
                                    "equals": game['name']
                                }
                            },
                            {
                                "property": "appid",
                                "rich_text": {
                                    "equals": str(game['appid'])
                                }
                            }
                        ]
                    }
                ]
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
                            "start": start_play.date().isoformat(),
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
            create_page(new_game_pageData)["id"]

        else:
            game_props = game_page.get('properties')  # notion game page properties

            # check if playtime_forever is greater than 'hours played' column
            prev_hours = game_props['Hours Played']['number']
            if prev_hours == format_playtime_hrs(game['playtime_forever']):
                print("No change in playtime for", game['name'])
                continue

            achievements = get_user_achievements_for_game(STEAM_ID, game['appid'])
            achievements = achievements['playerstats'].get('achievements', None)

            pageData = {
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
                            "start": game_props['Dates Played']['date']['start'],
                            "end": last_played.date().isoformat() if game_props['Status']['status']['name'] == "Completed" else None,
                        }
                    },
                    "Last Played": {
                        "date": {
                            "start": last_played.isoformat(),
                            "time_zone": "America/New_York"
                        }
                    },
                    "Hours Played": {
                        "number": format_playtime_hrs(game['playtime_forever'])
                    },
                    "Progress": {
                        "type": "number",
                        "number": get_achievement_percentage(achievements)
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

            # check if cover img is there
            if game_page['cover'] == None or game_page['icon'] == None:
                pageData['icon'] = {
                    "type": "external",
                    "external": {
                        "url": get_game_img_url(game['appid'], game['img_icon_url'])
                    }
                }
                pageData['cover'] = {
                    "type": "external",
                    "external": {
                        "url": get_game_img_url(game['appid'])
                    }
                }

            update_page(game_page["id"], pageData)

    # TODO: any Steam games not updated should be set to 'Taking a break'
    # do this once a week

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


# recent_games = get_recently_played_games(STEAM_ID).get('games', [])
# print(recent_games)
# id = recent_games[0]['appid']
# test = get_owned_games(STEAM_ID, [id])
# timestamp = test['response']['games'][0]['rtime_last_played']
# test = datetime.datetime.fromtimestamp(timestamp)
# print(test)
