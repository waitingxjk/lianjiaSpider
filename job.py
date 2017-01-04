from Crawler.Configuration.Conf import Conf
from Crawler.Database import MySQL
from Crawler.Crawl import craw


def crawl(conf: str, init=False):
    """
    :param conf: Configuration file
    :param url: Url for the city
    :param init: Indicator to init database
    :return:
    """
    Conf.initialize(conf)

    MySQL.initialize(Conf.mysql(), init)

    for job in Conf.jobs_fresh():
        craw(job)

if __name__ == "__main__":
    crawl("../config.conf")
