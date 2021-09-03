from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import hashlib
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo']
new_goods = db.new_goods


chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    executable_path='./chromedriver.exe', options=chrome_options)

driver.get('https://www.mvideo.ru/')

time.sleep(5)

section = driver.find_element_by_xpath(
    "//h2[contains(text(), 'Новинки')]/ancestor::div[3]")
actions = ActionChains(driver)
actions.move_to_element(section).perform()


btn = driver.find_element_by_xpath(
    "//h2[contains(text(), 'Новинки')]/ancestor::div[3]//a[contains(@class, 'i-icon-fl-arrow-right')]")

while True:
    time.sleep(2)
    items = driver.find_elements_by_xpath(
        "//h2[contains(text(), 'Новинки')]/ancestor::div[3]//li[contains(@class, 'gallery-list-item')]")

    for item in items:
        data = {}
        data['item'] = item.text

        hash_obj = hashlib.sha1()
        hash_obj.update(repr(data).encode('utf-8'))  # хэшируем id
        id = hash_obj.hexdigest()
        data['_id'] = id
        try:
            new_goods.insert_one(data)  # пишем в базу только уникальный id
        except:
            next

    try:
        test = driver.find_element_by_xpath(
            "//h2[contains(text(), 'Новинки')]/ancestor::div[3]//a[contains(@class, 'i-icon-fl-arrow-right disabled')]")
        break
    except NoSuchElementException:
        btn.click()


driver.close()
driver.quit()


def test_query():
    count = 0
    for i in new_goods.find():
        pprint(i)
        count += 1
    print(f'получено {count} товаров')


test_query()
