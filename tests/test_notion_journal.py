import pytest
from unittest.mock import Mock

import notion_daily_journal as journal
from notion_daily_journal import *



@pytest.mark.parametrize('has_events', [False, True])
def test_gcal(monkeypatch, has_events):
    start = datetime.datetime(2023, 5, 18, tzinfo=datetime.timezone.utc)
    end = start + datetime.timedelta(days=1)
    events = [
        {
            'summary': 'Afternoon meeting',
            'start': start + datetime.timedelta(hours=14),
            'end': start + datetime.timedelta(hours=15),
            'htmlLink': 'https://example.test/afternoon',
        },
        {
            'summary': 'Morning meeting',
            'start': start + datetime.timedelta(hours=9),
            'end': start + datetime.timedelta(hours=10),
            'htmlLink': 'https://example.test/morning',
        },
    ] if has_events else []
    get_events = Mock(return_value=events)
    monkeypatch.setattr(journal.cal_utils, 'get_today_timerange', lambda: (start, end))
    monkeypatch.setattr(journal, 'get_todays_events', get_events)
    # Use a portable, deterministic format while checking time rendering.
    monkeypatch.setattr(journal.utils, 'get_12hr_time_format_for_os', lambda _: '%H:%M')

    blocks, returned_events = journal.get_new_body_content_and_cal_events()

    get_events.assert_called_once_with(start, end)
    assert returned_events == events
    assert len(blocks) == len(events)
    if not has_events:
        assert blocks == []
        return
    assert [block['type'] for block in blocks] == ['bulleted_list_item'] * 2
    text = [block['bulleted_list_item']['rich_text'] for block in blocks]
    assert [parts[0]['text']['content'] for parts in text] == [
        'Morning meeting', 'Afternoon meeting',
    ]
    assert [parts[1]['text']['content'] for parts in text] == [
        ' (09:00 - 10:00)', ' (14:00 - 15:00)',
    ]
    assert text[0][1]['text']['link'] == {
        'type': 'url', 'url': 'https://example.test/morning',
    }


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
