# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
import logging
from datetime import datetime

import psycopg2
import configparser
import scrapy

from psycopg2.extensions import AsIs
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from crawl_douban_top250.scrapy_headers import get_image_headers
from itemadapter import ItemAdapter


# 创建数据库信息配置对象
db_info_config = configparser.ConfigParser()
# 读取配置文件
db_info_config.read('db_info.ini')


class PostgreSQLPipeline(object):
    def __init__(self, db_params):
        # 初始化信息
        self.db_params = db_params
        self.target_tb_name = AsIs('douban_books_doubanbooks')  # 设置要插入的表名称

    @classmethod
    def from_crawler(cls, crawler):
        # 从配置文件获取数据库信息
        db_params = {
            'dbname': db_info_config.get('database', 'name'),
            'user': db_info_config.get('database', 'user'),
            'password': db_info_config.get('database', 'password'),
            'host': db_info_config.get('database', 'host'),
            'port': db_info_config.get('database', 'port'),
        }
        return cls(db_params)

    def open_spider(self, spider):
        # 建立数据库连接
        conn = psycopg2.connect(**self.db_params)
        self.conn = conn
        spider.conn = conn

    def close_spider(self, spider):
        # 结束时，关闭连接
        self.conn.close()
        spider.conn.close()

    def get_existing_item_id(self, douban_id, cursor):
        # 获取douban_id对应的记录id
        cursor.execute("SELECT id FROM %s WHERE douban_id = %s", (self.target_tb_name, douban_id,))
        existing_item_id = cursor.fetchone()

        return existing_item_id[0] if existing_item_id else existing_item_id

    def extract_douban_id(self, book_url):
        # 从书本的url中提取出豆瓣的数据id，用来作区分数据的依据
        # todo 异常处理
        douban_id = re.match(r'.*douban.com.*/subject/(\d+)/', book_url)
        return douban_id.group(1)

    def update_data(self, item_id, item, cursor):
        # 更新已存在的记录
        sql = """
        UPDATE 
            %s 
        SET 
            title = %s,
            title_2 = %s, 
            book_url = %s,
            cover_path = %s,
            base_info = %s,
            author = %s,
            publisher = %s,
            publish_date = %s,
            price = %s,
            rating = %s,
            review_count = %s,
            summary = %s,
            is_readability = %s,
            update_date = %s
        WHERE id = %s;
        """
        values = (
            self.target_tb_name,
            item['title'],
            item['title_2'],
            item['book_url'],
            item['cover_path'],
            item['base_info'],
            item['author'],
            item['publisher'],
            item['publish_date'],
            item['price'],
            item['rating'],
            item['review_count'],
            item['summary'],
            item['is_readability'],
            datetime.now(),
            item_id
        )
        cursor.execute(sql, values)

    def create_data(self, item, cursor):
        # 创建新纪录
        now = datetime.now()
        sql = """
        INSERT INTO 
            %s 
        (
            title, title_2, douban_id, book_url, cover_path, base_info, 
            author, publisher, publish_date, price, rating, review_count,
            summary, create_date, update_date, is_readability
        )
        VALUES
        ( 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """
        values = (
            self.target_tb_name,
            item['title'],
            item['title_2'],
            item['douban_id'],
            item['book_url'],
            item['cover_path'],
            item['base_info'],
            item['author'],
            item['publisher'],
            item['publish_date'],
            item['price'],
            item['rating'],
            item['review_count'],
            item['summary'],
            now,
            now,
            item['is_readability']
        )
        cursor.execute(sql, values)

    def process_item(self, item, spider):
        # 处理数据，写入到数据库
        # 同时作去重处理

        # 每个游标是一个事物，在事物内插入数据，避免和前端用户操作冲突
        with self.conn.cursor() as cursor:
            item["douban_id"] = self.extract_douban_id(item["book_url"])
            existing_item_id = self.get_existing_item_id(item["douban_id"], cursor)
            try:
                # 获取douban_id
                # 去重处理
                if existing_item_id:
                    # 对已存在记录进行更新
                    self.update_data(existing_item_id, item, cursor)
                else:
                    # 新增未创建的记录
                    self.create_data(item, cursor)
                # 完成后提交事物
                self.conn.commit()
                return item

            except Exception as e:
                # 异常时回滚事物
                self.conn.rollback()
                raise DropItem(f"Error processing item: {e}  {item}, "
                               f"Pipeline: PostgreSQLPipeline, existing_item_id: {existing_item_id}")


class ImagePipeline(ImagesPipeline):
    # 图片管道
    def __init__(self, *args, **kwargs):
        super(ImagePipeline, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def file_path(self, request, response=None, info=None, *, item=None):
        return 'cover_path/{0}.jpg'.format(item['douban_id'])

    def get_media_requests(self, item, info):
        # Yield a request for each image URL in the item
        # yield scrapy.Request(item['cover_path'], headers=self.headers)
        yield scrapy.Request(item['cover_path'], headers=get_image_headers(item['cover_path']))

    def item_completed(self, results, item, info):
        # 将图片路径存储到item
        try:
            if results:
                item['cover_path'] = results[0][0] and results[0][1].get('path')

        except (IndexError, KeyError, AttributeError) as e:
            # 处理异常
            self.logger.error(f"An error occurred while extracting image path: {e}, item: {item}, result: {results}")

        return item


class DuplicatesPipeline(object):
    """
    去重管道
    提取并设置去重标识，进行去重处理
    """
    def __init__(self):
        # 创建一个一存在数据列表，存储douban_id
        self.existing_douban_id = set()

    def extract_douban_id(self, book_url):
        # 从书本的url中提取出豆瓣的数据id，用来作区分数据的依据
        # todo 异常处理
        douban_id = re.match(r'.*douban.com.*/subject/(\d+)/', book_url)
        return douban_id.group(1)

    def process_item(self, item, spider):
        # 去重操作
        item["douban_id"] = self.extract_douban_id(item["book_url"])
        if item["douban_id"] in self.existing_douban_id:
            raise DropItem(f"Data duplicate, please check item: {item}, Pipeline: DuplicatesPipeline")
        else:
            self.existing_douban_id.add(item["douban_id"])

        return item

