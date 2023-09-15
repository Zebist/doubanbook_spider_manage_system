# from celery import shared_task
from scrapy_management_system.celery import app
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawl_douban_top250.spiders import douban_book_spider

def start_spider(): 
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl(douban_book_spider.DoubanBookSpider)
    crawler.start()
    crawler.stop()

@app.task
def run_spider():
    try:
        p = Process(target=start_spider)
        p.start()
        p.join()
        # 任务执行成功
        result = "===================== 爬虫执行成功！====================="
        return result
    except Exception as e:
        # 任务失败，抛出异常
        raise e
    