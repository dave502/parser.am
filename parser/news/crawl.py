# import pathlib
# import sys
# import os
# sys.path.insert(0, os.getenv("ROOT_DIR", '/home/dave/DEV/ReestrParser'))

import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import settings
from spiders.news_spider import NewsSpider
# from logger.logger import setup_logger, setup_csv_logger, REGION_CHANGES, ALL_REGIONS_CSV
# from logger.data import headers


def run_spider():
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(NewsSpider)

    process.start(stop_after_crawl=True)


if __name__ == '__main__':
    #app_path = pathlib.Path(__file__).parent.resolve().parents[0]
    #setup_logger(LOGS, f'{app_path}/logs/{LOGS}.log')

    run_spider()

