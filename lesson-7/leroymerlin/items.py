# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def process_price(value):
    new_value = []
    for i in value:
        if i.isdigit():
            new_value.append(i)
    try:
        return int(''.join(new_value))
    except:
        return value

def process_photos(value):
    try:
        value = value.replace('w_82,h_82,', '')
    except:
        pass
    return value

def process_spec(value):
    try:
        value = value.replace('\n', '').replace(' ', '')
    except:
        pass
    if value != '':
        return value

def process_link(value):
    try:
        value = ''.join(value)
    except:
        pass
    return value

class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(input_processor=MapCompose(process_link), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(process_photos))
    specifications = scrapy.Field(input_processor=MapCompose(process_spec))