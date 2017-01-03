from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import random
import logging
from Crawler.Crawl import agents


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
        raise

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
    try:
        soup = page_soup(url)
        page_info = soup.find('div', {'class': 'page-box house-lst-page-box'})
        page_info_str = page_info.get('page-data').split(',')[0].split(':')[1]  # '{"totalPage":5,"curPage":1}'
        total_pages = int(page_info_str)

        # ==============================================================================
        estates = []
        for page in range(total_pages):
            if page > 0:
                soup = page_soup(url + "/pg%d/" % (page + 1))
            links = soup.find("ul", {"id": "house-lst"}).find_all("div", {"class": "col-1"})
            estates += list(link.a.get("href") for link in links)
        return estates

    except Exception as e:
        logging.error(e)


def craw(url: str):
    districts = crawl_districts_links(url + "/loupan")
    for k, v in districts.items():
        estate = craw_estate_links(url + v)
        print("%s 楼盘：%d" % (k, len(estate)))
        break
