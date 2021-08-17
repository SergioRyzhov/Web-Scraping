import requests
import json

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36', 'accept': '*/*'}

username = input('Input GitHub usernsme: ')
URL = f'https://api.github.com/users/{username}/repos'


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def save_file(data):
    with open('parsed_repos.json', 'w') as fw:
        json.dump(data, fw)


def parse():
    data = {}
    repos_list = []
    html = get_html(URL)
    if html.status_code == 200:
        for i in html.json():
            repos_list.append(i.get('name'))
        data.setdefault(username, repos_list)
        save_file(data)
    else:
        print(html.status_code)


parse()
