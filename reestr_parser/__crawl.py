from os import getenv
import sys
sys.path.insert(0, getenv("ROOT_DIR", '/home/dave/DEV/ReestrParser'))
print(sys.path)
import pathlib
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from db.queries import PaymentQuery
from logger.logger import setup_logger

import datetime

import settings
from spiders.rosreestrgovru import RosreestrgovruSpider
from logger.logger import REGION_CHANGES, setup_csv_logger, ALL_REGIONS_CSV
from logger.data import headers


app_path = pathlib.Path(__file__).parent.resolve().parents[0]
log = setup_logger("TEST", f'{app_path}/logs/TEST.log')
log.debug("test")
print("TEST")