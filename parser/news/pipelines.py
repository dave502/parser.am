# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
import os
from scrapy.exceptions import NotConfigured
from itemadapter import ItemAdapter
from dotenv import dotenv_values #load_dotenv
import re

class NewsPipeline:
    def __init__(self):
        
        self.mongo_client = None
        
        env = dotenv_values('.env')     
        MONGO_USER = os.environ.get('MONGO_ROOT_USERNAME', env.get('MONGO_ROOT_USERNAME'))
        MONGO_PASS = os.environ.get('MONGO_ROOT_PASSWORD', env.get('MONGO_ROOT_PASSWORD'))
        MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost:27017')
        MONGO_DB = os.environ.get('MONGO_DB', env.get('MONGO_DB'))
        
        if not all([MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_DB]):
            raise NotConfigured("Failed to get Mongodb credentials!")
        
        self.mongo_url = f'mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}'             
            
        # response = os.system("ping -c 1 " + MONGO_HOST)
        # if (response == 0):
        self.mongo_db = MONGO_DB
        
    
    def open_spider(self, spider):
        self.mongo_client = MongoClient(self.mongo_url)
        if not self.mongo_client:
            raise NotConfigured("Failed to create Mongodb client!")
        self.db = self.mongo_client[self.mongo_db]
        
    def close_spider(self, spider):
        self.client.close()
        
    def process_item(self, item, spider):
        
        item = {key: val.strip() for key, val in item.items()}
        
        # init mongo database
        collection: Collection = self.db[spider.name]
        
         # если новости ещё в базе нет -> запись в базу
        doc = collection.find_one({'url': item['url']})
        
        if not doc:
            
            if not item['img'].startswith('https:'):
                item['img'] = 'https://news.am/' + item['img']
            elif item['img'].startswith('https://www.youtube.com/embed/'):
                video_id = re.findall('https://www.youtube.com/embed/(.*)\?.*', item['img'])[0]
                item['img'] = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
            
            doc = collection.insert_one(item)
                
        return item
