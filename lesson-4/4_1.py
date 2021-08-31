from pymongo import MongoClient
import requests
from pprint import pprint
from lxml import html
from requests.api import head
from requests.models import Response
import hashlib


client = MongoClient('127.0.0.1', 27017)
db = client['lenta_ru']
news = db.news


URL = 'https://lenta.ru/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'accept': '*/*'
}

HOST = 'https://lenta.ru/'

response = requests.get('https://lenta.ru/', headers=HEADERS)


def get_contents():
    dom = html.fromstring(response.text)

    names = dom.xpath(
        '//section[contains(@class, "row")]/div/div[contains(@class, "item")]/h2/a/text() | //section[contains(@class, "row")]/div/div[contains(@class, "item")]/a/text()')
    links = dom.xpath(
        '//section[contains(@class, "row")]/div/div[contains(@class, "item")]/a/@href')
    dates = dom.xpath(
        '//section[contains(@class, "row")]/div/div[contains(@class, "item")]/h2/a/time/@datetime | //section[contains(@class, "row")]/div/div[contains(@class, "item")]/a/time/@datetime')

    for i in range(10):
        data = {}
        data['host'] = HOST
        data['name'] = names[i].replace('\xa0', ' ')
        data['link'] = HOST + links[i]
        data['date'] = dates[i]

        hash_obj = hashlib.sha1()
        hash_obj.update(repr(data).encode('utf-8'))  # хэшируем id
        id = hash_obj.hexdigest()
        data['_id'] = id
        try:
            news.insert_one(data)  # пишем в базу только уникальный id
        except:
            next


def check_query():
    count = 0
    for item in news.find():
        pprint(item)
        count += 1
    print(f'получено {count} новостей')


get_contents()
check_query()
