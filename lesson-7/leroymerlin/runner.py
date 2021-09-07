from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from spiders.lmru import LmruSpider
import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # query = input('Введите запрос: ')
    process.crawl(LmruSpider, query='ковер')
    process.start()