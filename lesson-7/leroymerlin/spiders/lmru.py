from lxml.html import parse
import scrapy
from scrapy.http import HtmlResponse
from items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']    

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}&suggest=true']
    
    def parse(self, response: HtmlResponse):
        ads_links = response.xpath("//a[@data-qa='product-image']")
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)
    

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('photos', '//img[@slot="thumbs"]/@src')
        loader.add_xpath('specifications', '//div[@class="def-list__group"]//text()')
        yield loader.load_item()

        # name = response.xpath("//h1/text()").get()
        # link = response.url
        # price = response.xpath("//span[@slot='price']/text()").get()
        # photos = response.xpath("//img[@slot='thumbs']/@src").getall()
        # yield LeroymerlinItem(name=name, link=link, price=price, photos=photos)
