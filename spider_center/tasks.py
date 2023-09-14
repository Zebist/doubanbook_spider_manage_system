from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging

from crawl_douban_top250.spiders import douban_book_spider


@shared_task
def run_spider():
    try:
        crawler = CrawlerProcess(get_project_settings())
        crawler.crawl(douban_book_spider.DoubanBookSpider)
        crawler.start()  # 运行爬虫

        # 如果任务成功完成，将状态设置为成功
        result = "===================== 爬虫执行成功！====================="
        return result
    except Exception as e:
        # 如果任务失败，将状态设置为失败，并记录异常信息
        raise e
    