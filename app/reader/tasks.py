import time
from io import BytesIO
from urllib.parse import urlparse

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.utils.text import slugify

from .services import scraper, translate

log = get_task_logger(__name__)


@shared_task
def scrape_article(article_pk):
    log.info(f'Scraping Article[{article_pk}]')
    from .models import Article, Site
    article = Article.objects.get(pk=article_pk)

    domain = urlparse(article.url).netloc
    try:
        site = Site.objects.get(domain=domain)
    except Site.DoesNotExist:
        site = None

    article_data = scraper.scrape(article)
    log.info(f'Saving scraped data for Article[{article_pk}]')
    Article.objects.filter(pk=article_pk).update(
        scraped_at=timezone.now(),
        site=site,
        **article_data,
    )
    log.info(f'Finished scraping Article[{article_pk}]')
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
    slug = slugify(article.title)
    filename = f'{slug}.mp3'
    s3_key = get_s3_key(article, filename)
    bucket.upload_fileobj(audio_buffer, s3_key, upload_config)
    log.info(f'Done uploading Article[{article_pk}] audio content.')

    article.audio_file.name = s3_key
    article.uploaded_at = timezone.now()
    article.save()
    # update_podcast.delay(article_pk)


@shared_task
def update_podcast():
    upload_config = {
        'ContentType': 'application/xml',
        'ACL': 'public-read'
    }
