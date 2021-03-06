from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

ps = CrawlerProcess(settings)

ps.crawl('nordstorm')
ps.start()