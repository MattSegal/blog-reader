import os

from feedgen.feed import FeedGenerator
from slugify import slugify
import boto3

from scraper import get_posts
from tts import text_to_speech_mp3

IGNORE_CACHE = False
BUCKET_NAME = 'blog-to-speech'
WEB_ROOT = 'https://s3-ap-southeast-2.amazonaws.com/blog-to-speech/'
bucket = boto3.resource('s3').Bucket(BUCKET_NAME)


def main():
    print('Scraping posts...', end='')
    posts = get_posts()
    print('done.')

    if not os.path.exists('public/media'):
        os.mkdir('public/media')

    print(f'Translating posts...')
    # content, title, author, posted_at, channel_name
    for post in posts:
        paragraphs = add_intro_paragraph(post)
        filename = slugify(post['title']) + '.mp3'
        path = os.path.join('public', 'media', filename)
        title = post['title']
        post['filename'] = filename
        if not os.path.exists(path) or IGNORE_CACHE:
            print(f'\tTranslating {title} into {filename}')
            text_to_speech_mp3(paragraphs, path)
        else:
            print(f'\tTranslation for {title} already exists.')

    print('Writing podcast manifest...', end='')
    create_podcast_manifest(posts)
    print('done.')

    print('Uploading files to S3...', end='')
    upload()
    print('done.')

def add_intro_paragraph(post):
    start = (
        '{title}. '
        'This article, written by {author}, was posted on {channel_name} on {posted_at}. '
        'Let\'s begin.'
    ).format(**post)
    return [start, *post['content']]

def upload(path='public'):
    files = (
        os.path.join(path, node) for node in os.listdir(path)
        if os.path.isfile(os.path.join(path, node))
    )
    folders = (
        os.path.join(path, node) for node in os.listdir(path)
        if os.path.isdir(os.path.join(path, node))
    )
    for folder in folders:
        upload(folder)

    for filename in files:
        with open(filename, 'rb') as f:
            print('\tUploading {}... '.format(filename), end='')
            key = filename.replace('public/', '')
            bucket.upload_fileobj(f, key, {
                'ContentType': get_content_type(filename),
                'ACL': 'public-read'
            })
            print('done')

def get_content_type(filename):
    if filename.endswith('.mp3'):
        return 'audio/mpeg'
    elif filename.endswith('.xml'):
        return 'application/xml'

def create_podcast_manifest(posts):


    gen = FeedGenerator()
    gen.load_extension('podcast')
    gen.title('Blog to Speech')
    gen.description('Blogs read to you by a computer.')
    gen.language('en-US')
    gen.author({
        'name': 'Matt Segal',
        'email': 'mattdsegal@gmail.com',
    })
    gen.webMaster('mattdsegal@gmail.com')
    gen.ttl(24 * 60 * 60)  # Minutes
    gen.link({'href': WEB_ROOT, 'rel': 'self'})
    # gen.image

    for post in posts:
        url = WEB_ROOT + 'media/' + post['filename']
        entry = gen.add_entry()
        entry.id(url)
        entry.enclosure(url, 0, 'audio/mpeg')
        entry.title(post['title'])
        entry.description(post['description'])
        entry.published(post['posted_at'])
        entry.author({'name': post['author']})
        entry.link({'href': post['url']})
        entry.ttl(24 * 60 * 60)  # Minutes

    gen.rss_str(pretty=True)
    gen.rss_file('public/podcast.xml')


if __name__ == '__main__':
    main()
