from feedgen.feed import FeedGenerator
from django.conf import settings

WEB_ROOT = f'https://s3-ap-southeast-2.amazonaws.com/{settings.AWS_STORAGE_BUCKET_NAME}/'


def write_manifest(articles, out_file):
    gen = FeedGenerator()
    gen.load_extension('podcast')
    write_meta_info(gen)
    for article in articles:
        write_article(article, gen)

    gen.rss_file(out_file)


def write_article(article, gen):
    file_url = f'{WEB_ROOT}{article.audio_file.name}'
    entry = gen.add_entry()
    entry.id(article.url)
    entry.enclosure(file_url, str(len(article.audio_file)), 'audio/mpeg')
    entry.title(article.title)
    entry.description(article.description)
    entry.published(article.posted_at.isoformat())
    entry.author({'name': article.author})
    entry.link({'href': article.url})
    entry.ttl(24 * 60 * 60)  # Minutes


def write_meta_info(gen):
    gen.title('Blog to Speech')
    gen.description('Blogs read to you by a computer.')
    gen.language('en')
    gen.author({
        'name': 'Matt Segal',
        'email': 'mattdsegal@gmail.com',
    })
    gen.webMaster('mattdsegal@gmail.com')
    gen.ttl(24 * 60 * 60)  # Minutes
    gen.link({'href': 'https://blogreader.com.au'})
