from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData, Float, Sequence, BigInteger, Integer

import logging


class MySQLClass:
    USED_HOUSE_INFO = "USED_HOUSE_INFO"
    USED_HOUSE_PRICE = "USED_HOUSE_PRICE"
    USED_CELL_INFO = "USED_CELL_INFO"

    def __init__(self):
        self.metadata = MetaData()

        self.UsedHouseInfo = Table(self.USED_HOUSE_INFO, self.metadata,
                                   Column("id", BigInteger, Sequence(self.USED_HOUSE_INFO), primary_key=True),
                                   Column("house_id", String(50)),
                                   Column("title", String(200)),
                                   Column("link", String(200)),
                                   Column("cell_name", String(100)),
                                   Column("years", String(200)),
                                   Column("house_type", String(50)),
                                   Column("area", Float),
                                   Column("direction", String(50)),
                                   Column("floor", Integer),
                                   Column("tax_type", String(200)),
                                   Column("total_price", String(200)),
                                   Column("unit_price", String(200)),
                                   Column("follow_info", String(200)),
                                   Column("valid_date", String(50)),
                                   Column("valid_flag", String(20)),
                                   )
        self.UsedHousePrice = Table(self.USED_HOUSE_PRICE, self.metadata,
                                    Column("id", BigInteger, Sequence(self.USED_HOUSE_PRICE), primary_key=True),
                                    Column("house_id", String(50)),
                                    Column("date", String(50)),
                                    Column("total_price", String(200)),
                                    )
        self.UsedHousePrice = Table(self.USED_CELL_INFO, self.metadata,
                                    Column("id", BigInteger, Sequence(self.USED_CELL_INFO), primary_key=True),
                                    Column("title", String(200)),
                                    Column("link", String(200)),
                                    Column("district", String(50)),
                                    Column("business_circle", String(50)),
                                    Column("tag_list", String(200)),
                                    )

        self.engine = None
        self._cache = {}

    def initialize(self, settings, init):
        con = "mysql://{user}:{password}@{host}:{port}/{schema}?charset=utf8".format(**settings)
        self.engine = create_engine(con, echo=False)

        if init:
            logging.info("Dropping and creating all the tables.")
            self.metadata.drop_all(self.engine)
            self.metadata.create_all(self.engine)

    ###################################################################################################################
    def select(self, desc: str, stmt):
        """Execute selection"""
        #
        ret = None
        try:
            conn = self.engine.connect()
            if desc:
                logging.info("Do selection: %s." % desc)
            ret = conn.execute(stmt).fetchall()
            conn.close()
        except Exception as ex:
            logging.error(ex)
            raise
        return ret

    class _Cached:
        def __init__(self, stmt, desc):
            self.stmt = stmt
            self.desc = desc
            self.records = []

        def reset(self):
            self.records = []

    def register(self, key, stmt, desc):
        if key in self._cache.keys():
            return
        self._cache[key] = self._Cached(stmt, desc)

    def cache(self, key, **record):
        self._cache[key].records += [record]

    def commit(self, keys=None):
        """Commit cached records by keys"""
        if not keys:
            keys = list(self._cache.keys())
        elif isinstance(keys, str):
            keys = [keys]
        with self.engine.begin() as trans:
            for key in keys:
                cached = self._cache[key]
                if not cached.records:
                    continue
                if cached.desc:
                    logging.info("Commit %d records: %s." % (len(cached.records), cached.desc))
                trans.execute(cached.stmt, cached.records)
                cached.reset()

    def dispose(self):
        self.engine.dispose()


MySQL = MySQLClass()


