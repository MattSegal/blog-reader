from datetime import datetime

import requests
from bs4 import BeautifulSoup

PARSE_URL = 'https://outlineapi.com/v2/parse_article'


def scrape(article, site=None):
    parsed_data = get_parsed_article(article.url)
    print(parsed_data)
    article_data = {
        'title': parsed_data['title'],
        'posted_at': get_posted_at(parsed_data),
        'author': parsed_data['author'],
        'description': get_description(parsed_data),
        'content': get_content(parsed_data),
    }
    return article_data


def get_parsed_article(url):
    resp = requests.get(PARSE_URL, params={'source_url': url})
    resp.raise_for_status()
    resp_payload = resp.json()
    assert resp_payload['success'], resp_payload
    return resp_payload['data']


def get_content(parsed_data):
    soup = BeautifulSoup(parsed_data['html'], 'html5lib')
    return '\n'.join([p for p in soup.text.split('\n') if p])


def get_posted_at(parsed_data):
    try:
        # January 09, 2019
        date_format = '%B %d, %Y'
        posted_at = datetime.strptime(parsed_data['date'], date_format)
    except (ValueError, TypeError):
        posted_at = None

    return posted_at


def get_description(parsed_data):
    return (
        'This article, written by {author}, '
        'was published on {site_name} '
        'on {date}. You can find more at {domain}.'
    ).format(**parsed_data)
