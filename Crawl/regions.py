from Crawl import *


def crawl_region_list(url: str):
    """
    Crawl regions from given url
    :param url:
    :return:
    """
    try:
        req = Request(url, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urlopen(req, timeout=50).read()
        soup = BeautifulSoup(source_code, 'lxml')
    except (HTTPError, URLError) as e:
        logging.error(e)
        raise
    except Exception as e:
        logging.error(e)
        raise

    regions = []
    try:
        page_info = soup.find('div', {'class': 'page-box house-lst-page-box'})
    except AttributeError as e:
        page_info = None

    if page_info == None:
        return None