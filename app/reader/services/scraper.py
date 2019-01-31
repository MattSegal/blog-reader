
from goose3 import Goose


def scrape(article):
    goose = Goose()
    article = goose.extract(url=article.url)
    content = '\n'.join([p for p in article.cleaned_text.split('\n') if p])
    article_data = {
        'title': article.title,
        'posted_at': article.publish_date,
        'description': article.meta_description,
        'author': ' and '.join(article.authors) or None,
        'content': content,
    }
    return article_data
