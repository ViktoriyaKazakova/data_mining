# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from pymongo import MongoClient
import scrapy


class FacebookscraperPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.fb_graph
        self.seen = {}

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)

        fb_id = item.get('fb_id')
        self.seen[fb_id] = self.seen.get(fb_id, 0) + 1
        if self.seen[fb_id] == 2:
            spider.crawler.engine.close_spider(self, reason=f'Есть совпадение.')
        return item