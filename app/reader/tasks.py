import time
from io import BytesIO
from urllib.parse import urlparse

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
import boto3

from .services import scraper, translate, podcast

log = get_task_logger(__name__)


@shared_task
def scrape_article(article_pk):
    log.info(f'Scraping Article[{article_pk}]')
    from .models import Article, Site
    article = Article.objects.get(pk=article_pk)

    domain = urlparse(article.url).netloc
    site, _ = Site.objects.get_or_create(
        domain=domain,
        defaults={
            'default_author': 'unknown author',
            'name': domain,
        }
    )
    article_data = scraper.scrape(article, site)

    log.info(f'Saving scraped data for Article[{article_pk}]')
    Article.objects.filter(pk=article_pk).update(
        scraped_at=timezone.now(),
        site=site,
        **article_data,
    )
    log.info(f'Finished scraping Article[{article_pk}]')
    if not article.uploaded_at:
        translate_article.delay(article_pk)


@shared_task
def translate_article(article_pk):
    log.info(f'Translating Article[{article_pk}]')
    from .models import Article, Site, get_s3_key
    article = Article.objects.get(pk=article_pk)
    if not article.scraped_at:
        log.info(f'Article[{article_pk}] cannot be translated - not yet scraped.')
        return

    # Translate the article text to an MP3 file.
    start = time.time()
    audio_buffer = BytesIO()
    translate.text_to_speech_mp3(article, audio_buffer)
    seconds = int(time.time() - start)
    log.info(f'Article[{article_pk}] audio content was translated in {seconds}s')

    # Upload the MP3 to AWS S3.
    log.info(f'Uploading Article[{article_pk}] audio content.')
    s3_storage = article.audio_file.storage
    bucket = s3_storage.bucket
    upload_config = {
        'ContentType': 'audio/mpeg',
        'ACL': 'public-read'
    }
    slug = slugify(article.title)[:80]
    filename = f'{slug}.mp3'
    s3_key = get_s3_key(article, filename)
    bucket.upload_fileobj(audio_buffer, s3_key, upload_config)
    log.info(f'Done uploading Article[{article_pk}] audio content.')

    article.audio_file.name = s3_key
    article.uploaded_at = timezone.now()
    article.save()
    if not article.manifested_at:
        update_podcast.delay()


@shared_task
def update_podcast():
    log.info('Creating new podcast manifest')
    from .models import Article
    articles = (
        Article.objects
        .filter(uploaded_at__isnull=False)
        .order_by('requested_at')
    )
    bucket = boto3.resource('s3').Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    text_buffer = BytesIO()
    podcast.write_manifest(articles, text_buffer)
    text_buffer.seek(0)
    s3_key = 'podcast.xml'
    upload_config = {
        'ContentType': 'application/xml',
        'ACL': 'public-read'
    }
    bucket.upload_fileobj(text_buffer, s3_key, upload_config)
    log.info('Podcast manifest published.')
    articles.update(manifested_at=timezone.now())
