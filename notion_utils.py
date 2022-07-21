# a set of Notion specific utility methods

def get_page_name(page, title_property='Name'):
    title = "".join(
        title_item['text']['content'] for title_item in page['properties'][title_property]['title']
    )
    return title
