import pytest
from notion_daily_journal import *



def test_gcal():
    a,b = get_new_body_content_and_cal_events()


class TestEventTags:
    """Test check_for_event_tags() function"""
    
    def test_no_tags(self):
        # input
        events_today_info = [
            {'summary': 'Travel to VAUGHAN - HWY 407 terminal', 'calendar': '1. Personal', 'htmlLink': 'https://www.google.com/calendar/event?eid=dHRsMG0wcGNrajZodm9kaGxpaGpxdjJnZjhfMjAyMzA1MThUMTAzMDAwWiBmb3JyZXN0aGVybWFuMTNAbQ&ctz=America/Toronto', 'start': datetime.datetime(2023, 5, 18, 6, 30, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))), 'end': datetime.datetime(2023, 5, 18, 8, 30, 38, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))}, 
            {'summary': 'Travel to Job (VIVA Transit)', 'calendar': '1. Personal', 'htmlLink': 'https://www.google.com/calendar/event?eid=dThwOG5jMmZjNHFza3NnNXFhZHFtdGE4aWdfMjAyMzA1MThUMTIyODAwWiBmb3JyZXN0aGVybWFuMTNAbQ&ctz=America/Toronto', 'start': datetime.datetime(2023, 5, 18, 8, 28, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))), 'end': datetime.datetime(2023, 5, 18, 8, 45, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))},
            {'summary': 'HOTS with Preteckt Team', 'calendar': '1. Personal', 'htmlLink': 'https://www.google.com/calendar/event?eid=MjI0M3ZudnM1dXZhbTBnZHM3bGtraWZmNm9fMjAyMzA1MTlUMDEwMDAwWiBmb3JyZXN0aGVybWFuMTNAbQ&ctz=America/Toronto', 'start': datetime.datetime(2023, 5, 18, 21, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))), 'end': datetime.datetime(2023, 5, 18, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))}
        ]

        # output
        tags = []

        assert check_for_event_tags(events_today_info) == tags


    def test_check_for_event_tags(self):
        # input
        events_today_info = [
            {'summary': 'Travel to VAUGHAN - HWY 407 terminal', 'calendar': '1. Personal', 'htmlLink': 'https://www.google.com/calendar/event?eid=dHRsMG0wcGNrajZodm9kaGxpaGpxdjJnZjhfMjAyMzA1MThUMTAzMDAwWiBmb3JyZXN0aGVybWFuMTNAbQ&ctz=America/Toronto', 'start': datetime.datetime(2023, 5, 18, 6, 30, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))), 'end': datetime.datetime(2023, 5, 18, 8, 30, 38, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))}, 
            {'summary': 'Grocery Shopping', 'calendar': '1. Personal', 'htmlLink': 'https://www.google.com/calendar/event?eid=dThwOG5jMmZjNHFza3NnNXFhZHFtdGE4aWdfMjAyMzA1MThUMTIyODAwWiBmb3JyZXN0aGVybWFuMTNAbQ&ctz=America/Toronto', 'start': datetime.datetime(2023, 5, 18, 8, 28, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))), 'end': datetime.datetime(2023, 5, 18, 8, 45, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))},
            {'summary': 'Fencing Practice', 'calendar': '1. Personal', 'htmlLink': 'https://www.google.com/calendar/event?eid=MjI0M3ZudnM1dXZhbTBnZHM3bGtraWZmNm9fMjAyMzA1MTlUMDEwMDAwWiBmb3JyZXN0aGVybWFuMTNAbQ&ctz=America/Toronto', 'start': datetime.datetime(2023, 5, 18, 21, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))), 'end': datetime.datetime(2023, 5, 18, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))},
            {'summary': '1-on-1 with Matt', 'calendar': '1. Personal', 'htmlLink': 'https://www.google.com/calendar/event?eid=MjI0M3ZudnM1dXZhbTBnZHM3bGtraWZmNm9fMjAyMzA1MTlUMDEwMDAwWiBmb3JyZXN0aGVybWFuMTNAbQ&ctz=America/Toronto', 'start': datetime.datetime(2023, 5, 18, 21, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))), 'end': datetime.datetime(2023, 5, 18, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))}
        ]

        # output
        tags = ['Groceries 🛒','Fencing 🤺','1-on-1']

        assert check_for_event_tags(events_today_info) == tags