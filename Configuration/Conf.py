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

    def jobs_fresh(self):
        jobs = []
        for section in self.conf.sections():
            if section.startswith("fresh_house"):
                sec = self.conf[section]
                email = sec.get("email")
                jobs += [{
                    "url": sec["url"],
                    "email": email
                }]
        return jobs

    @classmethod
    def initialize_log(cls):
        import logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] [%(funcName)s: line %(lineno)s]- %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

Conf = Configuration()
