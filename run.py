import os

from slugify import slugify

import scrapers
from tts import text_to_speech_mp3

IGNORE_CACHE = False
CHANNELS = [
    ('Local Posts', scrapers.posts),
    # ('Slate Star Codex', scrapers.ssc),
]


def main():
    for channel_name, scraper_module in CHANNELS:
        print(f'Scraping posts from {channel_name}\n')
        scraper = scraper_module.Scraper()
        scraper.scrape()
        channel_slug = slugify(channel_name)
        if not os.path.exists('media'):
            os.mkdir('media')

        channel_dir = os.path.join('media', channel_slug)
        if not os.path.exists(channel_dir):
            os.mkdir(channel_dir)

        print(f'\nTranslating posts from {channel_name}\n')
        # content, title, author, posted_at, channel_name
        for post in scraper.posts:
            paragraphs = add_intro_paragraph(post)
            filename = slugify(post['title']) + '.mp3'
            path = os.path.join(channel_dir, filename)
            title = post['title']
            if not os.path.exists(path) or IGNORE_CACHE:
                print(f'Translating {title} into {filename}')
                text_to_speech_mp3(paragraphs, path)
            else:
                print(f'Translation for {title} already exists.')


def add_intro_paragraph(post):
    start = (
        '{title}. '
        'This article, written by {author}, was posted on {channel_name} on {posted_at}. '
        'Let\'s begin.'
    ).format(**post)
    return [start, *post['content']]


if __name__ == '__main__':
    main()
