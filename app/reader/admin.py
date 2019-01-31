from django.contrib import admin
from django.contrib.messages import constants as messages

from .models import Article, Site
from .tasks import scrape_article, translate_article, update_podcast

admin.site.register(Site)


@admin.register(Article)
class Article(admin.ModelAdmin):
    list_display = (
        'url',
        'site',
        'title',
        'requested_by',
        'requested_at',
        'posted_at',
        'scraped_at',
        'manifested_at',
        'uploaded_at',
    )
    actions = ['scrape', 'translate', 'manifest']

    def scrape(self, request, queryset):
        for photo in queryset:
            scrape_article.delay(photo.pk)

        self.message_user(request, 'Scraping tasks dispatched.', level=messages.INFO)

    scrape.short_description = 'Scrape articles'

    def translate(self, request, queryset):
        for photo in queryset:
            translate_article.delay(photo.pk)

        self.message_user(request, 'Translation tasks dispatched.', level=messages.INFO)

    translate.short_description = 'Translate articles'

    def manifest(self, request, queryset):
        update_podcast.delay()
        self.message_user(request, 'Podcast update dispatched.', level=messages.INFO)

    manifest.short_description = 'Update podcast manifest'
