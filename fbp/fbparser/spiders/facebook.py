# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest, Request
from facebookscraper.items import FacebookProfileItem
from facebookscraper.items import FacebookProfileLoader


class FbSpider(scrapy.Spider):
    name = 'fb'
    allowed_domains = ['mbasic.facebook.com', 'facebook.com']
    start_url = ['https://mbasic.facebook.com/']
    about_url = 'https://mbasic.facebook.com/{}/about'
    friends_url = 'https://mbasic.facebook.com/{}?v=friends'
    urls_to_ids = []

    def __init__(self, login, pwd, target_users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.pwd = pwd
        self.target_users = target_users
        self.depth = 0

    def parse(self, response):
        return FormRequest.from_response(
            response,
            formxpath='//form[contains(@action, "login")]',
            formdata={'email': self.login, 'pass': self.pwd},
            callback=self.parse_users
        )

    def parse_users(self, response):
        for user in self.target_users:
            url = f'https://facebook.com/{user}'
            yield response.follow(url, callback=self.parse_user)

    def parse_user(self, response):
        friend_of = response.meta.get('friend_of')
        loader = FacebookProfileLoader(item=FacebookProfileItem(), response=response)
        loader.add_xpath('fb_id', '//meta[@property="al:android:url"]/@content', re='profile/(\d+)')
        loader.add_xpath('name', '//title/text()')
        loader.add_value('friend_of', friend_of)
        user = loader.load_item()
        user_fb_id = user.get('fb_id')
        yield Request(self.friends_url.format(user_fb_id), callback=self.get_friends,
                            meta={'friend_of': friend_of, 'user': user_fb_id})

        yield user

    def get_friends(self, response):
        friend_of = response.meta.get('friend_of')
        user = response.meta.get('user')

        friends = response.xpath(
            '//table[@role="presentation"]/tbody/tr[.//td[@style="vertical-align: middle"]]/td[2]/a')

        for friend in friends:
            url = friend.xpath('.//@href').get()
            yield Request(f'https://facebook.com{url}', callback=self.parse_user,
                          meta={'friend_of': user})

        next_page = response.xpath('//a[.//span[contains(text(), "Просмотреть больше друзей")]]/@href').get()

        if next_page:
            yield Request(response.urljoin(next_page), callback=self.get_friends,
                          meta={'user': user, 'friend_of': friend_of})