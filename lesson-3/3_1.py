from requests.models import Response
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import hashlib


client = MongoClient('127.0.0.1', 27017)
db = client['hh_ru']
vacancies = db.vacancies


URL = 'https://hh.ru/search/vacancy/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'accept': '*/*'
}
HOST = 'https://hh.ru'
FILTER = '/search/vacancy/?clusters=true&no_magic=true&ored_clusters=true&items_on_page=20&enable_snippets=true&salary=&st=searchVacancy'
request_job = input('Input the job: ')


def get_html(url, params=None):
    response = requests.get(url,
                            headers=HEADERS, params=params)
    return response


def get_digit_from_text(txt):
    temp = []
    for ch in txt:
        if ch.isdigit():
            temp.append(ch)
    return int(''.join(temp))


# def save_file(data, req):
#     with open(f'jobs_list_{request_job}.json', 'w', encoding='utf-8') as fw:
#         json.dump(data, fw)


def get_pages_count(html):
    soup = bs(html, 'html.parser')
    all_items = get_digit_from_text(soup.find(
        'div', {'class': 'novafilters-header'}).text.replace('\xa0', ''))
    return int(all_items / 20) + 1


def salary_sep(salary):
    first_salary = []
    last_salary = []
    salary = salary.replace('\u202f', '')
    if '–' in salary or '-' in salary or ('от' in salary and 'до' in salary):
        salary_next_index = 0
        for ind, i in enumerate(salary):
            if i.isdigit() and i != '-' and i != 'до':
                first_salary.append(i)
            else:
                salary_next_index = ind
                break
        for i in salary[salary_next_index:]:
            if i.isdigit():
                last_salary.append(i)
    elif salary.strip() == '':
        first_salary = None
        last_salary = None
        currency = None
    else:
        if 'до' in salary:
            for i in salary:
                if i.isdigit():
                    last_salary.append(i)
        else:
            for i in salary:
                if i.isdigit():
                    first_salary.append(i)
    if salary != '':
        currency = salary.split()[-1]
    if first_salary != None and first_salary != []:
        first_salary = int(''.join(first_salary))
    else:
        first_salary = None
    if last_salary != None and last_salary != []:
        last_salary = int(''.join(last_salary))
    else:
        last_salary = None
    return first_salary, last_salary, currency


count_vacancies = 0


def get_content(html):
    soup = bs(html, 'html.parser')
    # print(soup)
    jobs = soup.find_all('div', {'class': 'vacancy-serp-item'})
    # job_list = []
    for job in jobs:
        job_data = {}
        info = job.find(
            'div', {'class': 'vacancy-serp-item__info'})
        # print(info)
        name = info.find('a').text
        link = info.find('a').get('href')
        try:
            salary = job.find(
                'div', {'class': 'vacancy-serp-item__sidebar'}).text
        except:
            salary = ''

        salary_set = salary_sep(salary)
        job_data['name'] = name
        job_data['link'] = link
        job_data['start salary'] = salary_set[0]
        job_data['last salary'] = salary_set[1]
        job_data['currency'] = salary_set[2]
        job_data['site'] = HOST

        hash_obj = hashlib.sha1()
        hash_obj.update(repr(job_data).encode('utf-8'))  # хэшируем id
        id = hash_obj.hexdigest()
        job_data['_id'] = id
        try:
            vacancies.insert_one(job_data)  # пишем в базу только уникальный id
        except:
            next


def parse():
    params = {'text': f'{request_job}', 'page': 0}
    html = get_html(URL, params)
    if html.status_code == 200:
        pages_count = get_pages_count(html.text)
        for page in range(pages_count + 1):
            params['page'] = page
            print(f'парсинг страницы {page} из {pages_count}...')
            html = get_html(HOST+FILTER, params)
            get_content(html.text)
    else:
        print('error')


def salary_query():
    input_data = int(input('Input requered salary: '))
    count = 0
    for item in vacancies.find({'$or': [{'start salary': {'$gt': input_data}}, {'last salary': {'$gt': input_data}}]}):
        pprint(item)
        count += 1
    print(f'получено {count} вакансий')


parse()
salary_query()
