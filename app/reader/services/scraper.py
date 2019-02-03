from datetime import datetime

from goose3 import Goose


def scrape(article, site):
    goose = Goose()
    scraped_data = goose.extract(url=article.url)
    author = get_author(scraped_data, site)
    article_data = {
        'title': scraped_data.title,
        'posted_at': get_posted_at(scraped_data),
        'description': get_description(scraped_data, site, author),
        'author': author,
        'content': get_content(scraped_data),
    }
    return article_data


def get_posted_at(scraped_data):
    try:
        posted_at = datetime.strptime(scraped_data.publish_date, '%Y-%m-%dT%H:%M:%S%z')
    except (ValueError, TypeError):
        posted_at = None

    return posted_at


def get_content(scraped_data):
    paras = scraped_data.cleaned_text.split('\n')
    return '\n'.join([p for p in paras  if p])


def get_author(scraped_data, site):
    return (
        ' and '.join(scraped_data.authors) or
        site.default_author
    )


def get_description(scraped_data, site, author):
    if scraped_data.meta_description:
        return scraped_data.meta_description
    else:
        if scraped_data.publish_date:
            # 2013-04-18T07:47:26+00:00 to April 18, 2013
            posted_at = (
                datetime
                .strptime(scraped_data.publish_date.split('T')[0], '%Y-%m-%d')
                .strftime('%B %-d, %Y')
            )
        else:
            posted_at = 'an unknown time'

        return (
            f'This article, written by {author}, '
            f'was published on {site.name} '
            f'on {posted_at}. You can find more at {site.domain}.'
        )
