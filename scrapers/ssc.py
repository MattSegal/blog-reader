import requests
from bs4 import BeautifulSoup

POST_URLS = [
    'https://slatestarcodex.com/2013/04/18/floor-employment/',
    'https://slatestarcodex.com/2018/08/30/bureaucracy-as-active-ingredient/',
    'https://slatestarcodex.com/2019/01/14/too-many-people-dare-call-it-conspiracy/',
    'https://slatestarcodex.com/2018/09/13/the-omnigenic-model-as-metaphor-for-life/',
    'https://slatestarcodex.com/2018/10/04/next-door-in-nodrumia/',
    'https://slatestarcodex.com/2018/10/22/cognitive-enhancers-mechanisms-and-tradeoffs/',
    'https://slatestarcodex.com/2018/10/24/nominating-oneself-for-the-short-end-of-a-tradeoff/',
    'https://slatestarcodex.com/2018/11/13/preschool-much-more-than-you-wanted-to-know/',
    'https://slatestarcodex.com/2018/11/16/the-economic-perspective-on-moral-standards/',
    'https://slatestarcodex.com/2018/12/18/fallacies-of-reversed-moderation/',
    'https://slatestarcodex.com/2018/12/19/refactoring-culture-as-branch-of-government/',
]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
}

class Scraper:

    def __init__(self):
        self.posts = []

    def scrape(self):
        for post_url in POST_URLS:
            print(f'Fetching {post_url}')
            html = self.fetch_post(post_url)
            post = self.parse_post(html)
            self.posts.append(post)

    def fetch_post(self, url):
        """
        Fetch post from URL, returns HTML
        """
        resp = requests.get(url, headers=HEADERS)
        return resp.text

    def parse_post(self, html):
        """
        Read post data from
        """
        soup = BeautifulSoup(html, 'html5lib')
        # Get main post body
        post = soup.find('div', id='pjgm-content')
        # Remove comments
        post.find('div', id='comments').decompose()

        def class_text(class_name):
            return post.find(class_=class_name).text

        content = (
            class_text('pjgm-postcontent')
            .replace('\t', '')
            .split('\n')
        )
        # Remove empty strings
        content = [p for p in content if p]
        return {
            'channel_name': 'Slate Star Codex',
            'content': content,
            'title': class_text('pjgm-posttitle'),
            'posted_at': class_text('entry-date'),
            'author': class_text('author'),
        }
