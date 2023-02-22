import requests
import os
# load environment variables
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('STEAM_API_KEY')  # steam credentials
STEAM_ID = os.getenv('STEAM_ID')

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


def get_owned_games(player_id):
    interface = 'IPlayerService'
    method = 'GetOwnedGames'
    version = 'v0001'
    format = 'json'

    url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&steamid={player_id}'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code)

    data = result.json()
    return data


def get_user_stats_for_game(player_id, appid):
    interface = 'ISteamUserStats'
    method = 'GetUserStatsForGame'
    version = 'v0002'
    format = 'json'

    url = f'{base_url}/{interface}/{method}/{version}/?key={API_KEY}&format={format}&appid={appid}&steamid={player_id}'

    result = requests.get(url)
    if (result.status_code != 200):
        print(result.status_code)

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
        print(result.status_code)

    data = result.json()
    return data


def get_game_img_url(appid, hash):
    return f'http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg'


# data = get_owned_games(STEAM_ID)
# game_ids = [game.get("appid") for game in data['response']['games']]
# print(game_ids)


# for id in game_ids:
#     get_user_achievements_for_game(STEAM_ID, id)
#     break


# data = get_recently_played_games(STEAM_ID)
# print(data)
