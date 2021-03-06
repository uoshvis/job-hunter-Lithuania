import argparse
import bs4 as bs
import re
import requests

from datetime import datetime
from random import randint
from time import sleep

from city_codes import city_codes


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' +
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

base_url = (
    'http://www.cv.lt/employee/announcementsAll.do?' +
    'city={city_code}&regular=true&state=true&text={keyword}&page={page}')


def get_soup(keyword, city, page_number):

    if city:
        city_code = _get_city_code(city)
        if not city_code:
            print('City code not found')
    else:
        city_code = ''

    source = requests.get(
        base_url.format(
            keyword=keyword,
            city_code=city_code,
            page=str(page_number)
        ),
        headers=headers
    )

    soup = bs.BeautifulSoup(source.text, 'lxml')

    return soup


def find_pages_range(soup):
    result = soup.find("span", class_='paging-top')
    max_page = 1
    try:
        max_page = max([int(s) for s in result.get_text().split() if s.isdigit()])
    except AttributeError as exp:
        print('Dude! Error', exp)

    return max_page


def _format_result(result):
    result.replace('\n', '')
    result.replace('\t', '')
    result.replace(u'\xa0', u' ')
    result.rstrip()

    return result


def scrape_ad_page(url):
    """Scrapes a single add page
    :param url: url of single ad page
    :type url: str
    :returns: dict of single add data
    """
    responsibilities = None
    qualifications = None
    benefits = None
    jobad_expiration = None
    contact_person = None
    contact_email = None

    source = requests.get(url, headers=headers)
    soup = bs.BeautifulSoup(source.text, 'lxml')
    headings_2 = soup.find_all('h2')

    job_text = soup.find("div", class_="jobTxtRp")

    if job_text:
        job_text = job_text.get_text()

    for heading_2 in headings_2:
        if heading_2:
            heading_2_text = heading_2.get_text()
            if heading_2_text == 'Darbo pobūdis:':
                result = heading_2.find_next_sibling()
                responsibilities = ''
                for rez in result:
                    if rez.string:
                        responsibilities += rez.string + ' '
                responsibilities = _format_result(responsibilities)

            if heading_2_text == 'Reikalavimai:':
                result = heading_2.find_next_sibling()
                qualifications = ''
                for rez in result:
                    if rez.string:
                        qualifications += rez.string + ' '
                qualifications = _format_result(qualifications)

            if 'siūlo' in heading_2_text:
                result = heading_2.find_next_sibling()
                benefits = ''
                for rez in result:
                    if rez.string:
                        benefits += rez.string + ' '
                benefits = _format_result(benefits)

    job_table = soup.find('table', id='jobTxtRTable')
    job_table = job_table.find_all('tr')

    for row in job_table:
        td = row.find_all('td')
        for data in td:
            if 'iki' in data.get_text():
                if data.find_next_sibling():
                    jobad_expiration = data.find_next_sibling().get_text()
                    jobad_expiration = jobad_expiration.replace('.', '-')
                    jobad_expiration = datetime.strptime(jobad_expiration, '%Y-%m-%d')
            if data.get_text() in ['Contact person:', 'Kontaktinis asmuo:']:
                if data.find_next_sibling():
                    contact_person = data.find_next_sibling().get_text()
            if data.get_text() in ['El. paštas:', 'E-mail:']:
                if data.find_next_sibling():
                    contact_email_line = str(data.find_next_sibling())
                    match = re.search(r'[\w\.\-\_]+@[\w\.\-\_]+\.\w+', contact_email_line)
                    contact_email = match.group(0)

    return_data = {
        'responsibilities': responsibilities,
        'qualifications': qualifications,
        'benefits': benefits,
        'jobad_expiration': jobad_expiration,
        'contact_person': contact_person,
        'contact_email': contact_email,
        'job_text': job_text
    }

    return return_data


def scrape_list_page(soup):
    prefix = 'http://www.cv.lt'
    scraped_ads = []

    list_ads = soup.find_all("tr", class_='data')

    for ad in list_ads:
        # find position
        position = ad.find('a', itemprop='title').get_text()

        # find company
        company = ad.find('a', itemprop='hiringOrganization')
        company = company.get_text()
        company = company.replace('"', '')
        company = company.replace('\'', '')

        # find date posted
        date_posted = ad.find('meta', itemprop='datePosted')['content']
        date_posted = datetime.strptime(date_posted, '%Y-%m-%d')

        # find views
        views = ad.find('span', class_='visited').get_text()
        views = int(views.replace('.', ''))

        # find place
        place = ad.find('meta', itemprop='jobLocation')['content']

        # find ad url
        url_sri = ad.find('a', itemprop='title')

        # scrape single ad
        if url_sri:
            url_sri = prefix + url_sri['href']
            ad_id = int(re.search('\d-(\d+)', url_sri).groups()[0])
            ad_data = scrape_ad_page(url_sri)
            print('Scraping.. ', url_sri)
            sleep(randint(1, 4))

        # find salary if exists
        salary = ad.find('span', itemprop='baseSalary')
        if salary:
            salary = salary.get_text()

        list_data = {
            'ad_id': ad_id,
            'position': position,
            'company': company,
            'place': place,
            'views': views,
            'salary': salary,
            'date_posted': date_posted,

        }

        list_data.update(ad_data)
        print(list_data)
        scraped_ads.append(list_data)

    return scraped_ads


def _get_city_code(city):
    """Searches for city code
    param city: city name to search
    :type city: str
    :returns: str of city code if found else ''
    """
    city = city.capitalize()
    return str(city_codes.get(city, ''))


def main():

    page_number = 1

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

    soup_main = get_soup(
        keyword=args.keyword,
        city=args.city,
        page_number=page_number
    )
    page_range = find_pages_range(soup_main)
    print('Page range: {}'.format(page_range))

    while page_number <= page_range:
        print('Scannnig page: {}'.format(page_number))
        soup = get_soup(
            keyword=args.keyword,
            city=args.city,
            page_number=page_number
        )
        scrape_list_page(soup)

        page_number += 1
        sleep(randint(1, 5))
    print('Job Done')


if __name__ == '__main__':
    main()
