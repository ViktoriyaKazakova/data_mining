# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import urlencode, urljoin
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    variables_base = {'fetch_mutual': 'false', "include_reel": 'true', "first": 100}
    followers = {}
    posts = {}
    post_comments = {}
    post_commentors = []

    def __init__(self, user_links, login, pswrd, *args, **kwargs):
        self.user_links = user_links
        self.login = login
        self.pswrd = pswrd
        self.query_hash = 0
        super().__init__(*args, *kwargs)

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            'https://www.instagram.com/accounts/login/ajax/',
            method='POST',
            callback=self.parse_users,
            formdata={'username': self.login, 'password': self.pswrd},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_users(self, response: HtmlResponse):
        j_body = json.loads(response.body)
        if j_body.get('authenticated'):
            for user in self.user_links:
                yield response.follow(urljoin(self.start_urls[0], user),
                                      callback=self.parse_user,
                                      cb_kwargs={'user': user})

    def parse_user(self, response: HtmlResponse, user):
        user_id = self.fetch_user_id(response.text, user)
        user_vars = deepcopy(self.variables_base)
        user_vars.update({'id': user_id})
        self.query_hash = '58b6785bea111c67129decbe6a448951'
        yield response.follow(self.make_graphql_url(user_vars),
                              callback=self.parse_posts,
                              cb_kwargs={'user_vars': user_vars, 'user': user})

    def parse_posts(self, response: HtmlResponse, user_vars, user):
        data = json.loads(response.body)
        self.posts[user] = {'posts': data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')}
        for i in range(10):
            shortcode = self.posts.get(user).get('posts')[i].get('node').get('shortcode')
            user_vars = deepcopy(self.post_variables_base)
            user_vars.update({'shortcode': shortcode})
            self.query_hash = '865589822932d1b43dfe312121dd353a'
            yield response.follow(self.make_graphql_url(user_vars),
                                  callback=self.parse_post_commentors,
                                  cb_kwargs={'user_vars': user_vars, 'user': user})

    def parse_post_commentors(self, response: HtmlResponse, user_vars, user):
        data = json.loads(response.body)
        self.post_comments[user] = {
            'post_comments': data.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get('edges')}
        self.post_comments[user]['commentors'] = []
        if len(self.post_comments[user].get("post_comments")) > 0:
            if len(self.post_comments[user].get("post_comments")) > 9:
                limit = 9
            else:
                limit = len(self.post_comments[user].get("post_comments"))
            for i in range(limit):
                self.post_comments[user]['commentors'].append(
                    self.post_comments[user].get("post_comments")[i].get('node').get('owner').get('username'))
                print(self.post_comments[user].get("post_comments")[i].get('node').get('owner').get('username'))

    def parse_folowers(self, response: HtmlResponse, user_vars, user):
        data = json.loads(response.body)
        if not self.followers.get(user):
            self.followers[user] = {'followers': data.get('data').get('user').get('edge_followed_by').get('edges'),
                                    'count': data.get('data').get('user').get('edge_followed_by').get('count'),
                                    }
        else:
            self.followers[user]['followers'].extend(data.get('data').get('user').get('edge_followed_by').get('edges'))

        if data.get('data').get('user').get('edge_followed_by').get('page_info').get('has_next_page'):
            user_vars.update(
                {'after': data.get('data').get('user').get('edge_followed_by').get('page_info').get('end_cursor')})
            next_page = self.make_graphql_url(user_vars)

            yield response.follow(next_page, callback=self.parse_folowers,
                                  cb_kwargs={'user_vars': user_vars, 'user': user})

        if self.followers.get(user) and self.followers.get(user).get('count') == len(self.followers.get(user).get('followers')):
            pass

    def fetch_csrf_token(self, text):

        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):

        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, user_vars):

        result = '{url}query_hash={hash}&{variables}'.format(
            url=self.graphql_url, hash=self.query_hash,
            variables=urlencode(user_vars)
        )
        return result