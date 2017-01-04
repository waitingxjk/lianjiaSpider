from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import random
import logging
from Crawler.Crawl import agents
import sys


def page_soup(url: str):
    req = Request(url, headers=agents[random.randint(0, len(agents) - 1)])
    source_code = urlopen(req, timeout=50).read()
    soup = BeautifulSoup(source_code, 'lxml')
    return soup


def crawl_districts_links(url: str):
    """
    Crawl regions from given url
    :param url:
    :return:
    """
    try:
        soup = page_soup(url)
        districts = soup.find('div', {'class': 'option-list'}).find_all('a')
    except Exception as e:
        logging.error(e)
        sys.exit(-1)

    regions = {}
    for district in districts:
        if district.string == "不限":
            continue
        link = district.get('href')
        regions[district.string] = link

    return regions


def craw_estate_links(url: str):
    """
    Crawl information about estates in a district
    :param url:
    :return:
    """
    estates = []
    try:
        soup = page_soup(url)
        page_info = soup.find('div', {'class': 'page-box house-lst-page-box'})
        logging.debug(url)
        page_info_str = page_info.get('page-data').split(',')[0].split(':')[1]  # '{"totalPage":5,"curPage":1}'
        total_pages = int(page_info_str)
        # ==============================================================================
        for page in range(total_pages):
            if page > 0:
                soup = page_soup(url + "/pg%d/" % (page + 1))
            links = soup.find("ul", {"id": "house-lst"}).find_all("div", {"class": "col-1"})
            estates += list(link.a.get("href") for link in links)
    except Exception as e:
        logging.error(e)
        sys.exit(-1)
    return estates


def craw_estate(url: str):
    try:
        soup = page_soup(url)
        info = soup.find("div", {"class": "box-left-top"})
        title = info.a["title"]
        status = info.find("span", {"class": "state"}).string
        price = info.find("span", {"class": "junjia"}).string
        updated = info.find("p", {"class": "update"}).string

        print(title, status, price, updated)

    except Exception as e:
        logging.error(e)
        sys.exit(-1)

def craw(job: dict):
    url = job["url"]
    counter = 0
    districts = crawl_districts_links(url + "/loupan")
    for k, v in districts.items():
        links = craw_estate_links(url + v)
        for link in links:
            counter += 1
            craw_estate(url + link)
            if counter > 20:
                return
