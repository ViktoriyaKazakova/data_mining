import requests


#1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

USER_AGENT = 'Chrome/76.0.3809.100'

url_api = 'https://api.github.com/search/users'
username = 'ViktoriyaKazakova'

aditional_settings = 'simple=yes&per_page=1&page=1'

req = requests.get(f'{url_api}?q={username}&{aditional_settings}')
req.json()
file = open('out.json', 'w')
file.write(str(req.json()))
req.close()



