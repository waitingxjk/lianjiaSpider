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


def craw_estate(url: str):
    try:
        soup = page_soup(url)
        title = soup.find("div", {"class": "resb-name"}).string

        info = soup.find_all("ul", {"class": "x-box"})
        # Basic information
        basic = info[0].find_all("li")
        estate_type = basic[0].find_all("span")[1].string
        price = basic[1].find("span", {"class": "label-val"}).span.string
        address = basic[4].find("span", {"class": "label-val"}).string
        developer = basic[6].find("span", {"class": "label-val"}).string

        # Building information
        building = info[1].find_all("li")
        b_type = building[0].find("span", {"class": "label-val"}).string
        b_green = building[1].find("span", {"class": "label-val"}).string
        b_volume = building[3].find("span", {"class": "label-val"}).string
        b_wuye = building[5].find("span", {"class": "label-val"}).string
        b_residents = building[6].find("span", {"class": "label-val"}).string
        b_time_span = building[7].find("span", {"class": "label-val"}).string

        # Peripheral
        peripheral = info[2].find_all("li")
        p_wuye = peripheral[0].find("span", {"class": "label-val"}).string
        p_chewei = peripheral[1].find("span", {"class": "label-val"}).string
        p_wuyefei = peripheral[2].find("span", {"class": "label-val"}).string
        neighborhood = []
        for neighbor in peripheral[6].find("div", {"id": "around_txt"}).find_all("div"):
            category = neighbor["data-value"]
            if category == "其他":
                continue
            logging.debug(category)
            neighbors = neighbor.span.find_all("span")
            for item in neighbor.find_all("span", title=lambda x: x is not None):
                neighborhood += [(category, item["title"], item.string)]

        logging.info("%s, %s, %s, %s, %s" % (title, estate_type, price, address, developer))

    except Exception as e:
        logging.error("For url <%s>, there's error: %s" % (url, e))


def craw(job: dict):
    url = job["url"]
    districts = crawl_districts_links(url + "/loupan")
    for k, v in districts.items():
        links = craw_estate_links(url + v)
        for link in links:
            craw_estate(url + link + "xiangqing")