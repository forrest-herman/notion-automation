import json
import requests
import os
import urllib.parse
# load environment variables
from dotenv import load_dotenv
load_dotenv()

from firestore_methods import log_error

API_KEY = os.getenv('STEAM_API_KEY')  # steam credentials
STEAM_ID = os.getenv('STEAM_ID')
if STEAM_ID is None or API_KEY is None:
    raise Exception("Steam ID or API key not found in .env file.")

# see instructions here
# https://developer.valvesoftware.com/wiki/Steam_Web_API

base_url = 'http://api.steampowered.com'


def get_player_summaries(player_id):
    interface = 'ISteamUser'
    method = 'GetPlayerSummaries'
    version = 'v0002'
    format = 'json'

    url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&steamids={player_id}'

    result = requests.get(url)

    data = result.json()
    return data


def get_owned_games(player_id, appids_filter=None):
    interface = 'IPlayerService'
    method = 'GetOwnedGames'
    version = 'v0001'
    format = 'json'

    if appids_filter:
        input_json = {
            "steamid": player_id,
            "appids_filter": appids_filter,
        }
        input_json = json.dumps(input_json)
        url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&input_json={input_json}&include_appinfo=true'
    else:
        url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&steamid={player_id}&include_appinfo=true'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code)
        log_error(f'Steam API', result.text, 'get_owned_games', data={'reason': result.reason,'status_code': result.status_code, 'url': result.url, 'text': result.text})
        return None

    data = result.json()
    return data.get('response', {})


def get_user_stats_for_game(player_id, appid):
    interface = 'ISteamUserStats'
    method = 'GetUserStatsForGame'
    version = 'v0002'
    format = 'json'

    url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&appid={appid}&steamid={player_id}'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code)
        log_error(f'Steam API', result.text, 'get_user_stats_for_game', data={'reason': result.reason,'status_code': result.status_code, 'url': result.url, 'text': result.text})
        return None

    data = result.json()
    return data


def get_stats_for_game(appid):
    interface = 'ISteamUserStats'
    method = 'GetSchemaForGame'
    version = 'v0002'
    format = 'json'

    url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&appid={appid}'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code)
        log_error(f'Steam API', result.text, 'get_stats_for_game', data={'reason': result.reason,'status_code': result.status_code, 'url': result.url, 'text': result.text})
        return None

    data = result.json()
    return data


def get_recently_played_games(player_id):
    """Returns a list of games the player has played in the last two weeks.
    'total_count' the total number of unique games the user has played in the last two weeks. This is mostly significant if you opted to return a limited number of games with the count input parameter
    A 'games' array, with the following contents:
    - 'appid' Unique identifier for the game
    - 'name' The name of the game
    - 'playtime_2weeks' The total number of minutes played in the last 2 weeks
    - 'playtime_forever' The total number of minutes played "on record", since Steam began tracking total playtime in early 2009.
    - 'img_icon_url'
    - 'img_logo_url'
    """
    interface = 'IPlayerService'
    method = 'GetRecentlyPlayedGames'
    version = 'v0001'
    format = 'json'

    url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&steamid={player_id}'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code)
        log_error(f'Steam API', result.text, 'get_recently_played_games', data={'reason': result.reason,'status_code': result.status_code, 'url': result.url, 'text': result.text})
        return None

    data = result.json()
    return data.get('response', {})


def get_user_achievements_for_game(player_id, appid):
    interface = 'ISteamUserStats'
    method = 'GetPlayerAchievements'
    version = 'v0001'
    format = 'json'

    url = f'{base_url}/{interface}/{method}/{version}/?appid={appid}&key={API_KEY}&steamid={player_id}'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code, result.text, "No achievements found for appid:", appid)
        log_error(f'Steam API: No achievements found for appid: {appid}', result.text, 'get_user_achievements_for_game', data={'reason': result.reason,'status_code': result.status_code, 'url': result.url, 'text': result.text})
        return None
    
    data = result.json()
    return data


def get_game_img_url(appid, hash=None):
    if hash is None:
        return f'https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg'
    return f'http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg'


# data = get_owned_games(STEAM_ID)
# game_ids = [game.get("appid") for game in data['response']['games']]
# print(game_ids)


# for id in game_ids:
#     get_user_achievements_for_game(STEAM_ID, id)
#     break


# data = get_recently_played_games(STEAM_ID)
# print(data)
