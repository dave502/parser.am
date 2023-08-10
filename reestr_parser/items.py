# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReestrParserItem(scrapy.Item):

    id = scrapy.Field()  # field for mongo
    url = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field()
    region = scrapy.Field()
    objects = scrapy.Field()
    law = scrapy.Field()
    authority = scrapy.Field()
    year = scrapy.Field()

    solution_date = scrapy.Field()
    solution_act_num = scrapy.Field()
    solution_act_link = scrapy.Field()

    report_date = scrapy.Field()
    report_region = scrapy.Field()
    report_reality_type = scrapy.Field()
    report_quantity = scrapy.Field()
    report_project_date = scrapy.Field()
    report_project_date_start = scrapy.Field()
    report_project_date_end = scrapy.Field()
    report_check_act_link = scrapy.Field()
    report_intermediate_docs_link = scrapy.Field()
