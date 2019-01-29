import os
import json
from urllib.parse import urlparse

from goose3 import Goose
from slugify import slugify

from channels import channels

def get_posts():
    goose = Goose()

    with open('urls.txt', 'r') as f:
        urls = [u for u in f.read().split('\n') if u]

    posts = []
    for url in urls:
        domain = urlparse(url).netloc
        try:
            channel = channels[domain]
        except KeyError:
            channel = {
                'name': domain,
                'slug': 'custom',
                'default_author': None,
            }

        article = goose.extract(url=url)
        content = [
            p for p in article.cleaned_text.split('\n')
            if p
        ]
        post = {
            'url': url,
            'channel_name': channel['name'],
            'title': article.title,
            'posted_at': article.publish_date,
            'description': article.meta_description,
            'author': ''.join(article.authors) or channel['default_author'],
            'content': content,
        }

        channel_dir = os.path.join('posts', channel['slug'])
        if not os.path.exists(channel_dir):
            os.mkdir(channel_dir)

        filename = slugify(post['title']) + '.json'
        filepath = os.path.join(channel_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(post, f, indent='2')

        posts.append(post)

    return posts
