# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from jobparser.items import AvitoRealEstate

class AvtSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://avito.ru/rossiya/kvartiry']

    def parse(self, response):
        ads_links = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)
        pass

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=AvitoRealEstate(), response=response)
        loader.add_xpath('photos',
                         '//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url')
        loader.add_css('title', 'h1.title-info-title span.title-info-title-text::text')
        par_names = response.css('li.item-params-list-item span.item-params-label::text').extract()
        for i in range(len(par_names)):
            par_names[i] = par_names[i].replace(' ', '')

        par_data = response.css('li.item-params-list-item::text').extract()
        my_dict = {'Этаж:': 'floor',
                    'Этажейвдоме:': 'house_floors',
                    'Типдома:': 'house_type',
                    'Количествокомнат:': 'rooms',
                    'Общаяплощадь:': 'total_s',
                    'Жилаяплощадь:': 'living_s',
                    'Площадькухни:': 'kitchen_s',
                }

        result_dict = {}
        for i in range(len(par_names)):
            result_dict[my_dict[par_names[i]]] = par_data[i * 2 + 1]

        for keys in result_dict:
            loader.add_value(keys, result_dict[keys])
        print(1)
        yield loader.load_item()
