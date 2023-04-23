from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from reestr_parser import settings
from spiders.rosreestrgovru import RosreestrgovruSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(RosreestrgovruSpider)

    process.start()
