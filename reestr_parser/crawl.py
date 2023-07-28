import pathlib
import sys
sys.path.insert(0, '/home/dave/DEV/ReestrParser')

import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import settings
from spiders.rosreestrgovru import RosreestrgovruSpider
from logger.logger import setup_logger, REGION_CHANGES, setup_csv_logger, ALL_REGIONS_CSV
from logger.data import headers


def run_spider():
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(RosreestrgovruSpider)

    process.start(stop_after_crawl=True)


if __name__ == '__main__':
    app_path = pathlib.Path(__file__).parent.resolve().parents[0]
    setup_logger(REGION_CHANGES, f'{app_path}/logs/{REGION_CHANGES}.log')
    setup_csv_logger(ALL_REGIONS_CSV, f'{app_path}/logs/{datetime.datetime.today().date()} '
                                      f'{datetime.datetime.now().strftime("%H:%M")}.csv',
                     headers)

    run_spider()
    # # schedule.every().day.at("10:30", "Europe/Moscow").do(run_spider)
    # schedule.every(1).minutes.do(run_spider) #do(lambda: os.system('scrapy crawl spiders/rosreestrgovru'))
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
