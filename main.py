import bs4 as bs
import requests
import re
import sys

from time import sleep
from random import randint
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' +
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


def utf_encoder(input_raw):
    input_utf = str(input_raw.encode('utf-8'))
    encoded = input_utf.replace("\\x", "%")
    encoded = encoded.replace("'", "")
    encoded = encoded.lstrip('b')
    return encoded


def find_pages_range(soup):
    """
    :param soup: soup object search result page
    :returns: max page number of results
    """
    pages = soup.find("ul", {'class': "pages_ul_inner"})
    try:
        children = pages.find_all('a')
        for page in children:
            max = page.string
            print('==', max)
    except:
        max = 1
    return int(max)


def get_soup(city_name, keyword, page_number):
    """
    :params city_name:
    :params keyword:
    :params page_number:
    :returns: soup object of given search result page
    """

    if city_name and keyword:
        source = requests.get(
            'https://www.cvbankas.lt/?miestas=' + utf_encoder(city_name) +
            '&keyw=' + utf_encoder(keyword) +
            '&page=' + str(page_number), headers=headers)
    else:
        source = requests.get(
            'https://www.cvbankas.lt/?page=' + str(page_number), headers=headers)
    soup = bs.BeautifulSoup(source.text, 'lxml')

    return soup


def scrape_ad(url_link):
    """
    :param url_link: url of single ad page
    :returns: statistics of the single ad: views, candidates, ratio
    """
    ad_statistics = {}
    salary = None
    salary_from = None
    salary_to = None
    salary_avg = None
    salary_percent = None
    salary_info = None
    company = None
    place = None

    source = requests.get(url_link, headers=headers)
    soup = bs.BeautifulSoup(source.text, 'lxml')

    ad_id = int(re.findall(r"-\d+", url_link)[0].lstrip('-'))

    position = soup.find(
        'h1',
        {'class': 'heading1', 'id': 'jobad_heading1', 'itemprop': 'title'}).get_text()

    company = soup.find(
        'h2',
        {'id': 'jobad_company_title', 'itemprop': 'name'})
    if company:
        company = company.get_text()
        company = company.replace(',', '')
        company = company.replace('"', '')
        company = company.replace('\'', '')

    jobad_expiration = soup.find(
        'div',
        {'id': 'jobad_expiration'})['title']
    # jobad_expiration = re.search(r'\d{4}.\d{2}.\d{2}', jobad_expiration)
    # jobad_expiration = jobad_expiration.group().replace('.', '-')
    jobad_expiration = jobad_expiration.replace('.', '-')
    jobad_expiration = datetime.strptime(jobad_expiration, '%Y-%m-%d')

    candidates = soup.find_all('strong', {'class': "jobad_stat_value"})

    if len(candidates) == 1:
        ad_statistics['views'] = int(candidates[0].string)
        ad_statistics['candidates'] = 0
        ad_statistics['ratio'] = 0
    elif len(candidates) == 2:
        ad_statistics['views'] = int(candidates[0].string)
        if '>' not in candidates[1].string:
            ad_statistics['candidates'] = int(candidates[1].string)
            ratio = (ad_statistics['candidates'] / ad_statistics['views']) * 100
            ad_statistics['ratio'] = round(float(ratio), 2)
        else:
            ad_statistics['ratio'] = 'many_candidates'

    else:
        ad_statistics['views'] = 'Error'
        print('I have problems in find_candidates_statistics')
        #   raise ValueError('Candidates info list is not good for me')

    jobad = soup.find_all('div', {'class': 'jobad_txt'})

    place = jobad[0].find_all('a', {'class': 'js_ga_event'})
    if place:
        place = place[-1].get_text()

    responsibilities = soup.find(
        'div',
        {'class': 'jobad_txt', 'itemprop': 'responsibilities'})
    if responsibilities:
        responsibilities = responsibilities.get_text()
        responsibilities = responsibilities.replace('*', '')
        responsibilities = " ".join(responsibilities.replace(chr(8226), '').split())

    qualifications = soup.find(
        'div',
        {'class': 'jobad_txt', 'itemprop': 'qualifications'})
    if qualifications:
        qualifications = qualifications.get_text()
        qualifications = qualifications.replace('*', '')
        qualifications = " ".join(qualifications.replace(chr(8226), '').split())

    benefits = soup.find(
        'div',
        {'class': 'jobad_txt', 'itemprop': 'benefits'})
    if benefits:
        benefits = benefits.get_text()
        benefits = benefits.replace('*', '')
        benefits = " ".join(benefits.replace(chr(8226), '').split())

    sections = soup.find_all('section')
    for section in sections:
        heading = section.find('h4', {'class': 'heading4 pt30 pb5'})
        if heading and (heading.get_text() == 'Atlyginimas' or heading.get_text() == 'Salary'):
            salary_info = " ".join(
                section.find('div', {'class': 'jobad_txt'}).get_text().split())
            salary = re.findall(r'(\d+)', salary_info)
            if salary and len(salary) == 2:
                salary_from = int(salary[0])
                salary_to = int(salary[1])
            elif salary and len(salary) == 1:
                salary_from = int(salary[0])

    salary_avg_box = soup.find(
        'div',
        {'class': 'jobad_average_salary_box'})
    if salary_avg_box:
        salary_avg = re.findall(r"(\d+)€", salary_avg_box.get_text())
        if salary_avg:
            salary_avg = int(salary_avg[0])

        salary_percent = re.findall(r"(\d+)%", salary_avg_box.get_text())
        if salary_percent:
            salary_percent = int(salary_percent[0])
        else:
            salary_percent = None

    return_data = {
        'ad_id': ad_id,
        'position': position,
        'company': company,
        'jobad_expiration': jobad_expiration,
        'ad_statistics': ad_statistics,
        'place': place,
        'responsibilities': responsibilities,
        'qualifications': qualifications,
        'benefits': benefits,
        'salary_info': salary_info,
        'salary_from': salary_from,
        'salary_to': salary_to,
        'salary_avg': salary_avg,
        'salary_percent': salary_percent
    }
    print(return_data, '\n')
    return return_data


def scrape_list_page(soup):
    """
    :params soup: soup of single search result page
    :returns: list of candidates statistics from single
        search results page
    """
    scraped_ads = []

    job_links = soup.find_all('a', {'class': "list_a can_visited list_a_has_logo"})
    print('in scrape_list_page')
    print(job_links)
    if not job_links:
        job_links = soup.find_all(
            'a',
            {'class': "list_a can_visited list_vip_a"})
    for job_link in job_links:
        print('Scraping..', job_link['href'])
        scraped_ad = scrape_ad(job_link['href'])
        scraped_ads.append(scraped_ad)
        sleep(randint(1, 4))

    return scraped_ads


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    final_positions = []
    page_number = 1
    if len(sys.argv) == 3:
        city_name = sys.argv[2]
        keyword = sys.argv[1]
    else:
        city_name = None
        keyword = None
    soup = get_soup(city_name, keyword, page_number)
    page_range = find_pages_range(soup)
    print('page_range {}'.format(page_range))

    while page_number <= page_range:
        print('Scannnig page {}'.format(page_number))
        soup = get_soup(city_name, keyword, page_number)
        scraped_ads = scrape_list_page(soup)
        print('scraped ads', scraped_ads)
        page_number += 1
        sleep(randint(1, 5))
    print('Job Done')
