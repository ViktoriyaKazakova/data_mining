from bs4 import BeautifulSoup as bs
import requests


#Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайта
#superjob.ru и hh.ru. Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы).
#Получившийся список должен содержать в себе минимум:
#*Наименование вакансии
#*Предлагаемую зарплату (отдельно мин. и и отдельно макс.)
#*Ссылку на саму вакансию
#*Сайт откуда собрана вакансия

headers = {'User-agent':'Chrome/76.0.3809.100'}
url = 'https://spb.hh.ru/search/vacancy'

vacancy_name = input("Введите название вакансии:")
result_list = []

def parse_page(page):
    params = dict(area='113', page=str(page),customDomain=str(1))
    request = requests.get(f'{url}??L_is_autosearch=false&clusters=true&enable_snippets=true&text=\
    {vacancy_name}&page=0', headers=headers, params=params).text
    soup = bs(request, 'html.parser')
    div = soup.find_all('div', attrs={"class": "vacancy-serp-item__row vacancy-serp-item__row_header"})
    for item in div:
        name = item.findChildren("a" , recursive=True)[0].text
        link = item.findChildren("a" , recursive=True)[0].attrs['href']
        salary = item.findChildren("div" , recursive=True)[2].text.replace(u'\xa0', ' ')
        result_list.append({'Наименование': name, "Зарплата": salary, "Ссылка": link, 'Сайт': 'hh.ru'})


for i in range(0,10):
    parse_page(i)

print(result_list)


