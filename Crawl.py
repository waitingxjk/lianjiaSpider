from Configuration.Conf import Conf
from Database import MySQL


def crawl(conf: str, init=False):
    """
    :param conf: Configuration file
    :param init: Indicator to init database
    :return:
    """
    Conf.initialize(conf)

    MySQL.initialize(Conf.mysql(), init)

if __name__ == "__main__":
    crawl("./config.conf", init=True)
