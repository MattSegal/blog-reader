from django.db import models
from django.contrib.auth.models import User

from .tasks import scrape_article

class Site(models.Model):
    name = models.CharField(max_length=256)
    default_author = models.CharField(max_length=256)
    domain = models.CharField(max_length=256)

    def __str__(self):
        return self.name

def get_s3_key(instance, filename):
    return f'media/{filename}'


class Article(models.Model):
    url = models.URLField(max_length=1024, unique=True)
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)
    author = models.CharField(max_length=64, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    audio_file = models.FileField(upload_to=get_s3_key, null=True, blank=True)
    requested_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    requested_at = models.DateTimeField(auto_now=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(null=True, blank=True)
    manifested_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)

    def get_title(self):
        return self.title if self.title else self.url

    def get_status(self):
        if self.manifested_at:
            return 'Manifested'
        elif self.uploaded_at:
            return 'Translated'
        elif self.scraped_at:
            return 'Downloaded'
        else:
            return 'Requested'

    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            scrape_article.delay(self.pk)
