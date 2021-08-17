import requests
import json

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36', 'accept': '*/*'}
target_user = int(input('Input the target user_id to get sosieties: '))
token = input('Paste access_token: ')
params = {
    'user_id': target_user,
    'v': 5.52,
    'access_token': token,
    'extended': 1
}


def get_sosieties(params=None):
    respond = requests.get(
        f'https://api.vk.com/method/groups.get', headers=HEADERS, params=params)
    return respond


def save_file(data):
    with open(f'{target_user}.json', 'w') as fw:
        json.dump(data, fw)


def parse():
    data = {}
    groups_list = []
    html = get_sosieties(params)
    if html.status_code == 200:
        for i in html.json().get('response').get('items'):
            groups_list.append(i.get('name'))
        data.setdefault(target_user, groups_list)
        save_file(data)
    else:
        print(html.status_code)


parse()
