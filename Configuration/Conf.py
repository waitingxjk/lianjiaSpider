import configparser


class Configuration:
    def __init__(self):
        self.conf = configparser.ConfigParser()

    def initialize(self, filename):
        self.initialize_log()
        self.conf.read(filename)

    def mysql(self):
        conf = {}
        "mysql://{user}:{password}@{host}:{port}/{schema}?charset=utf8"
        conf["host"] = self.conf["mysql"]["host"]
        conf["port"] = self.conf["mysql"].get("port", 3306)
        conf["schema"] = self.conf["mysql"]["schema"]
        conf["user"] = self.conf["mysql"]["user"]
        conf["password"] = self.conf["mysql"]["password"]
        return conf

    @classmethod
    def initialize_log(cls):
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(funcName)s]- %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S')

Conf = Configuration()
