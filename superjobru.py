# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['https://www.superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python']

    def get_min_salary(self, salary):
        sal_min_1 = re.compile('от [0-9]+')
        if re.findall(sal_min_1, salary):
            min_salary = re.findall(sal_min_1, salary)
        else:
            min_salary = ''
        return min_salary

    def get_max_salary(self, salary):
        sal_max_1 = re.compile('до [0-9]+')
        if re.findall(sal_max_1, salary):
            max_salary = re.findall(sal_max_1, salary)
        else:
            max_salary = ''
        return max_salary

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-dalshe::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacancy = response.css('a.icMQ_ _1QIBo f-test-link::attr(href)').extract()
        for link in vacancy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        name = response.css('div.3mfro rFbjy s1nFK _2JVkc" h1.header::text').extract_first()
        salary = response.css('div.3mfro _2Wp8I ZON4b PlM3e _2JVkc::span').extract_first()
        salary = re.sub('\xa0', "", salary)
        min_salary = self.get_min_salary(salary)
        max_salary = self.get_max_salary(salary)
        url = response.request.url
        yield JobparserItem(name=name, min_salary=min_salary, max_salary=max_salary, url=url)