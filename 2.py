import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import lxml
import time
import random

#На основе материалов урока, сделать выборку объявлений с AVITO по категории недвижимость квартиры продажа, сохраняем:
#Имя пользователя который опубликовал объявление
#Ссылку на профиль пользователя
#Параметры объявления (метраж, этаж, и тд)
#Стоимость
#url адрес объявления


mongo_url = 'mongodb://localhost:27017'
client = MongoClient('localhost', 27017)
database = client.leson2

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/76.0.3809.100 Chrome/76.0.3809.100 Safari/537.36'



def req_ads(url):
    response = requests.get(url, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        price = soup.body.findAll('span', attrs={'class': 'js-item-price', 'itemprop': 'price'})[0].attrs.get('content')
    except IndexError:
        price = None
    result = {'user_name': soup.body.findAll('a', attrs = {'title':'Нажмите, чтобы перейти в профиль"'}),
              'price': int(price) if price and price.isdigit else None,
              'url': response.url,
              'link_user': [f'{base_url}{itm.find("a").attrs["href"]}' for itm in user_block],
              'params': [tuple(itm.text.split(':')) for itm in
                         soup.body.findAll('li', attrs={'class': 'item-params-list-item'})]
              }
    return result


base_url = 'https://www.avito.ru'
url = 'https://www.avito.ru/krasnodarskiy_kray/nedvizhimost'

response = requests.get(url, headers={'User-Agent': USER_AGENT})
soup = BeautifulSoup(response.text, 'lxml')
body = soup.html.body
user_block = body.findAll('div', attrs={'class': 'seller-info-name js-seller-info-name'})
result = body.findAll('h2', attrs={'data-marker': 'bx-recommendations-block-title'})
ads = body.findAll('div', attrs={'data-marker': 'bx-recommendations-block-item'})
urls = [f'{base_url}{itm.find("a").attrs["href"]}' for itm in ads]

collection = database.avito


for itm in urls:
    time.sleep(random.randint(1, 5))
    result = req_ads(itm)
    collection.insert_one(result)
