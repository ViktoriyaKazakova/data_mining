# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader


def to_int(value):
    if value.isdigit():
        return int(value)
    return value


class FacebookProfileLoader(ItemLoader):
    default_output_processor = TakeFirst()
    fbid_in = MapCompose(to_int)

class FacebookProfileItem(scrapy.Item):
    _id = scrapy.Field()
    fbid = scrapy.Field()
    name = scrapy.Field()
    friend_of = scrapy.Field()