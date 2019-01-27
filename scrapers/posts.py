import os

EXAMPLE_FILE = 'template.txt'

class Scraper:

    def __init__(self):
        self.posts = []

    def scrape(self):
        for post_file in os.listdir('posts'):
            if post_file == EXAMPLE_FILE:
                continue

            print(f'Parsing {post_file}')
            path = os.path.join('posts', post_file)
            with open(path, 'r') as f:
                text = f.read()

            post = self.parse_post(text)
            self.posts.append(post)

    def parse_post(self, text):
        """
        Read post data from
        """
        parts = text.split('\n')
        parts = [
            p for p in parts
            if p and not p.startswith('#')
        ]
        return {
            'channel_name': parts[0],
            'title': parts[1],
            'posted_at': parts[2],
            'author': parts[3],
            'content': parts[4:],
        }
