import argparse
import cvbankas_scraper as cvbankas
import cv_scraper as cv

from time import sleep
from random import randint


def main():
    SITES_AVAILABLE = [cv, cvbankas]

    parser = argparse.ArgumentParser(description='finds job postings')
    parser.add_argument(
        '-k',
        '--keyword',
        type=str,
        default='',
        help='keyword to search'
    )
    parser.add_argument(
        '-c',
        '--city',
        type=str,
        default='',
        help='city to search'
    )
    args = parser.parse_args()

    for site in SITES_AVAILABLE:
        page_number = 1
        get_soup = getattr(site, 'get_soup')
        soup = get_soup(
            city=args.city,
            keyword=args.keyword,
            page_number=page_number
        )
        find_pages_range = getattr(site, 'find_pages_range')
        page_range = find_pages_range(soup)
        print('Page range of {site} is {range}.'.format(
            site=site.__name__,
            range=page_range)
        )
        while page_number <= page_range:
            print('Scannnig page {}'.format(page_number))
            soup = get_soup(
                city=args.city,
                keyword=args.keyword,
                page_number=page_number
            )
            scraped_ads = getattr(site, 'scrape_list_page')(soup)
            print('scraped ads', scraped_ads)
            page_number += 1
            sleep(randint(1, 5))
        print('Job Done')


if __name__ == '__main__':
    main()
