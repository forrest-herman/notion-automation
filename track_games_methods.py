import datetime
from notion_api_methods import *
from tracking_games.steam_api_methods import *
# get_recently_played_games, get_game_img_url, STEAM_ID


database_id_games = 'ab34a11b1156466bb028ced90af23f96'

# helpers functions


def format_playtime_hrs(playtime_mins):
    if playtime_mins == 0:
        return None
    return round(playtime_mins / 60, 1)


def get_last_played(game):
    timestamp = game.get('rtime_last_played', 0)
    if timestamp == 0:
        return None
    last_played = datetime.datetime.fromtimestamp(timestamp)
    return last_played


def get_achievement_percentage(achievements):
    if achievements is None:
        return None
    total = len(achievements)
    # sum all true achievements
    count = sum(a['achieved'] == 1 for a in achievements)
    return round((count / total) * 100, 1)


def lookup_game_in_notion(steam_game):
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
                                "equals": steam_game['name']
                            }
                        },
                        {
                            "property": "appid",
                            "rich_text": {
                                "equals": str(steam_game['appid'])
                            }
                        }
                    ]
                }
            ]
        }
    }
    results = query_database_pages(database_id_games, query_game_page_payload)
    game_page = results[0] if len(results) > 0 else None
    return game_page


# main function
def update_games_list():
    recent_games = get_recently_played_games(STEAM_ID).get('games', [])

    for game in recent_games:
        # process the game data from the api query
        extra_game_info = get_owned_games(STEAM_ID, [game['appid']])['games'][0]
        game = game | extra_game_info  # merge the two dictionaries

        last_played = get_last_played(extra_game_info)
        start_play = last_played - datetime.timedelta(minutes=game['playtime_forever'])

        game_page = lookup_game_in_notion(game)

        if game_page is None:
            # game page doesn't exist, create it
            create_notion_game_page(game, last_played, start_play)
        else:
            game_props = game_page.get('properties')  # notion game page properties

            # check if playtime_forever is greater than 'hours played' column
            prev_hours = game_props['Hours Played']['number']
            if prev_hours == format_playtime_hrs(game['playtime_forever']):
                print("No change in playtime for", game['name'])
                continue

            achievements = get_user_achievements_for_game(STEAM_ID, game['appid'])
            achievements = achievements['playerstats'].get('achievements', None)

            update_notion_game_page(game, game_page, achievements)

    if datetime.date.today().weekday() == 6:  # is Sunday
        # do this once a week
        print("--------------------\nWeekly Game Update...\n--------------------")
        update_all_games(recent_games)

    return True
    # The End #


def update_all_games(recent_games=[]):
    all_steam_games = get_owned_games(STEAM_ID)['games']

    for game in all_steam_games:
        # check if the game is on the recent games list
        if game['appid'] in [g['appid'] for g in recent_games]:
            continue

        game_page = lookup_game_in_notion(game)
        if game_page is None:
            # create a new page for the game
            create_notion_game_page(game)
        else:
            # update the game page
            update_notion_game_page(game, game_page)


def update_notion_game_page(game, prev_page_data, achievements=None):
    last_played = get_last_played(game)

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
            "Status": {
                "type": "status",
                "status": {
                    "name": "Taking a break" if last_played else "Never Played"
                }
            },
            "Last Played": {
                "date": {
                    "start": last_played.isoformat(),
                    "time_zone": "America/New_York"
                } if last_played else None
            },
            "Hours Played": {
                "type": "number",
                "number": format_playtime_hrs(game['playtime_forever'])
            },
            "Progress": {
                "type": "number",
                "number": get_achievement_percentage(achievements) if achievements else None
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
    prev_status = prev_page_data['properties']['Status']['status']['name']
    if prev_status == "Completed":
        pageData['properties']['Status']['status']['name'] = "Completed"

    # check if cover img is there
    if prev_page_data['cover'] == None or prev_page_data['icon'] == None:
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

    update_page(prev_page_data["id"], pageData)
    print("Updated page for game:", game['name'])


def create_notion_game_page(game, last_played=None, start_play=None):
    # WORKS FOR STEAM GAMES
    pageData = {
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
                "url": get_game_img_url(game['appid'])
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
            "Game Store": {
                "type": "select",
                "select": {
                    "name": "Steam"
                }
            },
            "Last Played": {
                "date": {
                    "start": last_played.isoformat(),
                    "time_zone": "America/New_York"
                } if last_played else None
            },
            "Dates Played": {
                "date": {
                    "start": start_play.date().isoformat(),
                } if start_play else None
            },
            "Hours Played": {
                "type": "number",
                "number": format_playtime_hrs(game['playtime_forever']) if last_played else None
            },
            "Status": {
                "type": "status",
                "status": {
                    "name": "In progress" if last_played else "Never Played"
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

    # if last_played is None:
    #     props = ['Dates Played', 'Last Played', 'Hours Played']
    #     for prop in props:
    #         pageData.pop(prop, None)
    #     pageData['properties']['Status']['status']['name'] = "Never Played"

    print("Create new page for game:", game['name'])
    create_page(pageData)

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

def main():
    update_games_list()
    update_all_games()


if __name__ == '__main__':
    main()
