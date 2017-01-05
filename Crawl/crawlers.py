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
        if not page_info:
            logging.info("No page information found.")
            return estates
        page_info_str = page_info.get('page-data').split(',')[0].split(':')[1]  # '{"totalPage":5,"curPage":1}'
        total_pages = int(page_info_str)
        # ==============================================================================
        for page in range(total_pages):
            if page > 0:
                soup = page_soup(url + "/pg%d/" % (page + 1))
            links = soup.find("ul", {"id": "house-lst"}).find_all("div", {"class": "col-1"})
            estates += list(link.a.get("href") for link in links)
    except Exception as e:
        logging.error("For url <%s>, there's error: %s" % (url, e))
    return estates


def craw_estate(url):
    import json
    try:
        soup = page_soup(url)
        content = list(str(s.string) for s in soup.find_all("script") if str(s.string).find("bdLocalSearch") > -1)
        if not content:
            logging.info("Failed to find data for <%s>." % url)
            return
        data = content[0][content[0].find("{"):content[0].find(";")]
        info = json.loads(data)

        # Information keys
        # room_structure, open_stages, url
        basics = ["id", "city_id", "district_name", "resblock_name", "developer_company"]
        prop = ["property_company", "properright", "property_price"]
        address = ["longitude", "latitude", "address"]
        sales = ["average_price", "lowest_total_price", "price_confirm_time", "sale_status"]
        building = ["build_type", "house_type", "decoration"]
        stats = ["max_frame_area", "min_frame_area", "cubage_rate", "virescence_rate", "underground_car_num",
                 "overground_car_num", "carRatio"]
        time = ["open_date", "hand_over_time"]

        keys = basics + prop + address + sales + building + stats + time

        desc = dict((k, info[k]) for k in keys)
        logging.info(desc)
    except Exception as e:
        logging.error("For url <%s>, there's error: %s" % (url, e))


def craw(job: dict):
    url = job["url"]
    districts = crawl_districts_links(url + "/loupan")
    for k, v in districts.items():
        links = craw_estate_links(url + v)
        for link in links:
            craw_estate(url + link + "xiangqing")