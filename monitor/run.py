from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

ps = CrawlerProcess(get_project_settings())

ps.crawl('nordstorm')
ps.start()