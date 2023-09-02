# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from datetime import datetime

import scrapy


class DoubanBookItem(scrapy.Item):
    title = scrapy.Field()
    title_2 = scrapy.Field()
    douban_id = scrapy.Field()
    cover_path = scrapy.Field()
    book_url = scrapy.Field()
    base_info = scrapy.Field()
    author = scrapy.Field()
    publisher = scrapy.Field()
    publish_date = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    summary = scrapy.Field()
    create_date = scrapy.Field()
    update_date = scrapy.Field(default=datetime.now)
    is_readability = scrapy.Field()