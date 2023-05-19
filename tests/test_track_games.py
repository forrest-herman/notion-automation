import pytest
from track_games_methods import *


def test_format_playtime():
    assert format_playtime_hrs(playtime_mins=14141) == 235.7
    assert format_playtime_hrs(playtime_mins=0) == None


def test_get_last_played():
    game = {
        "appid": 400,
        "name": "Portal",
        "playtime_forever": 483,
        "img_icon_url": "cfa928ab4119dd137e50d728e8fe703e4e970aff",
        "has_community_visible_stats": True,
        "playtime_windows_forever": 483,
        "playtime_mac_forever": 0,
        "playtime_linux_forever": 0,
        "rtime_last_played": 1669865162
    }

    time = datetime.datetime(2022, 11, 30, hour=22, minute=26, second=2)

    assert get_last_played(game) == time
    assert get_last_played({"rtime_last_played": 0}) == None


def test_get_achievement_percentage():
    achievements = [
        {"name": "PORTAL_GET_PORTALGUNS","achieved": 1},
        {"name": "PORTAL_KILL_COMPANIONCUBE","achieved": 1},
        {"name": "PORTAL_ESCAPE_TESTCHAMBERS","achieved": 0},
        {"name": "PORTAL_BEAT_GAME","achieved": 1}
    ]

    assert get_achievement_percentage(achievements) == 75