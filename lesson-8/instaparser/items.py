# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    followers = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    photos = scrapy.Field()
    main_user = scrapy.Field()
