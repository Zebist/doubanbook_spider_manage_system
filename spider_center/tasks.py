from celery import shared_task
from scrapy import cmdline

@shared_task
def run_spider():
    # 运行爬虫
    cmdline.execute("scrapy crawl douban_book".split())