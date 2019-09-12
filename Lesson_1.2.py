import requests
#2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

headers = {'Authorization' : 'token OAUTH-TOKEN'}


r = requests.get('https://api.github.com/user', headers=headers)
r.json()
file = open('out2.json', 'w')
file.write(str(r.json()))
r.close()