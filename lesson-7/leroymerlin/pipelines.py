# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import scrapy
import os


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroy0709

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item._values)
        return item

class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                # img = img.replace('w_82,h_82,', '')
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)
    
    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item):
        return f'images/{item["name"]}' + os.path.basename(urlparse(request.url).path)
