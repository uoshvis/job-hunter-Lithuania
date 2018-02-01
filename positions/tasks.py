from celery import shared_task

from utils.main import search_positions


@shared_task
def scrape_ads(city, keyword):
    # TODO is it better connect to db using models?
    # like this User.objects.create_user(username=username, email=email)
    search_positions(city=city, keyword=keyword)
    return 'Searched for kw {kw} in city {city}.'.format(city=city, kw=keyword)
