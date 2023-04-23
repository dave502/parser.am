# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.collection import Collection
from settings import BD_PARAMS
from urllib.parse import urlparse
from urllib.parse import parse_qs

from telegram.informer import send_to_telegram


class ReestrParserPipeline:
    def __init__(self):
        client = MongoClient(**BD_PARAMS)
        self.mongo_base = client.reestr

    def process_item(self, item, spider):

        item['_id'] = self.get_url_id(item['url'])
        item = {field: value.strip() for (field, value) in item.items() if value}

        collection: Collection = self.mongo_base[spider.name]

        if doc := collection.find_one({'_id': item['_id']}):
            shared_items = {field: item[field] for field in item if item.get(field) != doc.get(field)}
            if shared_items:
                send_to_telegram(f"Изменения в документе {item['_id']}: \n {shared_items}")
                collection.update_one({'_id': item['_id']}, {'$set': shared_items})
        else:
            collection.insert_one(item)
        return item

    @staticmethod
    def get_url_id(url):
        parsed_url = urlparse(url)
        item_id = parse_qs(parsed_url.query).get("id")[0]
        return item_id
