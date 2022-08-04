# a set of Notion specific utility methods

def get_page_name(page, title_property='Name'):
    try:
        title = "".join(
            title_item['text']['content'] for title_item in page['properties'][title_property]['title']
        )
    except KeyError:
        title = page['properties'][title_property]['title'][0]['text']['content'] + '(!)'
    except:
        title = "Invalid title"
    return title
