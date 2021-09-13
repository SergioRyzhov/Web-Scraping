import scrapy
import re
import json
from scrapy.http import HtmlResponse
from items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = ''
    inst_pwd = ''
    parse_users = ['asdfghjkl.7786', 'sadfgsdfg646', 'sadfgsdfgsds']
    # posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    # graphql_url = 'https://www.instagram.com/graphql/query/?'
    api_url = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):  # логинимся
        # print()
        j_data = response.json()
        if j_data['authenticated']:
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_parse,
                    cb_kwargs={'username': user}
                )

    # запрос на подписчиков и на кого подписан юзер
    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        # url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
        url_followers = f'{self.api_url}{user_id}/followers/?count=12&search_surface=follow_list_page'
        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'followers_all': 'followers'},
            headers={'User-Agent': 'Instagram 155.0.0.37.107'}
        )

        url_following = f'{self.api_url}{user_id}/following/?count=12&search_surface=follow_list_page'
        yield response.follow(
            url_following,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'followers_all': 'following'},
            headers={'User-Agent': 'Instagram 155.0.0.37.107'}
        )

    # подмена ссылок на продолжение 12 следующих
    def user_followers_parse(self, response: HtmlResponse, username, user_id, followers_all):
        # print()
        j_resp = response.json()
        # page_info = j_data.get('data').get('user').get(
        #     'edge_owner_to_timeline_media').get('page_info')
        if j_resp['next_max_id']:
            max_id = j_resp['next_max_id']
            url_followers = f'{self.api_url}{user_id}/{followers_all}/?count=12&max_id={max_id}&search_surface=follow_list_page'
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'followers_all': 'followers_all'},
                headers={'User-Agent': 'Instagram 155.0.0.37.107'}
            )

        # Перебираем всех подписчиков и на кого подписан юзернейме и отправляем item в пайп
        for user in j_resp['users']:
            item = InstaparserItem(
                followers=followers_all,
                user_id=user['pk'],
                username=user['username'],                
                photos=user['profile_pic_url'],
                main_user=username,
            )
            yield item

    def fetch_csrf_token(self, text):
        # Получаем токен для авторизации
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        # get user ID from the JavaScript in HTML
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
