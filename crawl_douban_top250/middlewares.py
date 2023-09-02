# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
import json
import logging

import requests
from scrapy import signals, Request
from scrapy.utils.project import get_project_settings
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest

from .proxy_node import ProxyNode

settings = get_project_settings()

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class CrawlDoubanTop250SpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class CrawlDoubanTop250DownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ProxyMiddleware(RetryMiddleware):
    # 代理中间件，在重试时更换代理ip
    def __init__(self, *args, **kwargs):
        super(ProxyMiddleware, self).__init__(*args, **kwargs)
        # self.logger = logging.getLogger(__name__)
        self.proxy_url = settings["PROXY_URL"]
        self.proxy_list = []
        self.max_use_count = 4

    def extend_proxy_list(self, proxy_data_list):
        # 将请求到的代理列表格式化后保存
        for proxy_ob in proxy_data_list['data']:
            pn = ProxyNode(proxy_ob['ip'], proxy_ob['port'], self.max_use_count)
            self.proxy_list.append(pn)

    def refresh_proxy_list(self, proxy_url):
        # 刷新代理列表
        response = requests.get(proxy_url)
        json_data = response.json()
        try:
            if json_data['code'] == 1:
                self.extend_proxy_list(json_data)
            else:
                logging.warning(
                    f'Can not to retrieve proxy data. Status code: {response.status_code}, data: {json_data}')
        except requests.exceptions.RequestException as e:
            logging.warning(f'An error occurred during the request of proxy: {e}')
        except AttributeError as e:
            logging.warning(f'Attribute error: {e}')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')

    def set_proxy(self, request):
        # 设置代理
        if self.proxy_list:
            p_node = self.proxy_list.pop()
            request.meta['proxy'] = p_node.address
            request.meta['proxy_remain'] = p_node.max_count

    def process_request(self, request, spider):
        # 在第一次请求时添加代理
        if not self.proxy_url:
            return
        # 第一次请求时添加代理
        if 'proxy' not in request.meta:
            # 无可用代理，刷新代理列表
            if not self.proxy_list:
                self.refresh_proxy_list(self.proxy_url)
            # 设置代理
            self.set_proxy(request)

    def handle_proxy_remain(self, proxy_remain, request):
        # 每次请求将节点可用次数-1，防止超过限制数量，防止屏蔽
        if proxy_remain > 0:
            request.meta['proxy_remain'] -= 1

    def retry_request_page_with_new_proxy(self, request, reason, spider):
        # 启用了代理，且可用代理列表为空时，刷新代理列表
        if 'proxy' in request.meta and not self.proxy_list:
            self.refresh_proxy_list(self.proxy_url)
        self.set_proxy(request)
        res = self._retry(request, reason=reason, spider=spider)  # 重新请求
        return res

    def process_response(self, request, response, spider):
        # 每次请求时处理代理节点
        proxy_remain = request.meta.get('proxy_remain', 0)
        self.handle_proxy_remain(proxy_remain, request)

        # 遇到302响应时切换代理并重新请求
        if response.status == 302 or proxy_remain == 0:
            # 设置代理
            res = self.retry_request_page_with_new_proxy(request, "302 Redirecting response", spider)
            logging.warning(
                f"Received a 302 Redirecting response: {response} Switching to a new proxy: {request.meta['proxy']} ")
            if res:
                return res
            else:
                raise IgnoreRequest("This request is being ignored because it exceeded the maximum retry limit.")

        return response

    def process_exception(self, request, exception, spider):
        # 处理连接问题，例如拒绝连接或超时
        if isinstance(exception, ConnectionRefusedError):
            # 重试
            res = self.retry_request_page_with_new_proxy(request, "Connection refused", spider)
            logging.warning(
                f"Connection refused: {request.url} Switching to a new proxy: {request.meta['proxy']} ")

            return res


class CrawlRecordMiddleware(RetryMiddleware):
    # 爬取记录中间件，用来记录url的爬取结果
    def __init__(self, *args, **kwargs):
        super(CrawlRecordMiddleware, self).__init__(*args, **kwargs)
        # self.logger = logging.getLogger(__name__)

    def process_response(self, request, response, spider):
        # 每次返回结果时进行判断
        self.handle_record(request, response.status, spider)

        return response

    def handle_record(self, request, status_code, spider):
        """
        处理请求记录，在parse时，将url和请求结果记录到数据库，下次爬取时，会在初始化时将url取出
        这样即使遇到了请求失败，也可以分步把数据补全
        :param request: 本次的请求对象
        :param status_code: 本次的响应状态码
        :param spider: 爬虫对象
        :return:
        """
        # 豆瓣阅读的403是登录界面，不需要记录
        if status_code == 403:
            return
        url = request.url
        is_exist = self.check_is_exist(url, spider)
        # 根据数据库记录情况选择处理方法，已存在进行更新，未存在则进行创建记录
        handle_method = self.choice_handle_method(is_exist)
        # 执行操作，根据请求结果记录爬取结果
        handle_method(url, status_code==200, spider)

    def choice_handle_method(self, is_exist):
        """
        选择处理方法
        :param is_exist: 是否已在数据库
        :return: 处理方法
        """
        # 如果记录已存在数据库, 更新
        if is_exist:
            handle_method = self.update_to_database
        # 记录不存在，创建
        else:
            handle_method = self.insert_to_database

        return handle_method

    def check_is_exist(self, url, spider):
        """
        判断数据库是否已有记录
        :param url: 请求的url
        :param spider: 爬虫对象
        :return: True已有记录 False无记录
        """
        cursor = spider.conn.cursor()
        cursor.execute("""
                    SELECT url FROM douban_books_doubanbookcrawlrecord WHERE url = %s;
                """, (url, ))
        return bool(cursor.fetchone())

    def insert_to_database(self, url, flag, spider):
        """
        将记录插入到数据库
        :param url: url
        :param flag: 是否爬取成功
        :param spider: 爬虫对象
        :return:
        """
        try:
            with spider.conn.cursor() as cursor:
                insert_query = "INSERT INTO douban_books_doubanbookcrawlrecord (url, is_ok) VALUES (%s, %s);"
                cursor.execute(insert_query, (url, flag))
                spider.conn.commit()
        except Exception as e:
            spider.conn.rollback()
            logging.error(f"Add crawl record to database failed！ Please Check: {e}")

    def update_to_database(self, url, flag, spider):
        """
        更新数据库记录
        :param url: url
        :param flag: 是否爬取成功
        :param spider: 爬虫对象
        :return:
        """
        try:
            with spider.conn.cursor() as cursor:
                insert_query = "UPDATE douban_books_doubanbookcrawlrecord SET is_ok=%s WHERE url=%s;"
                cursor.execute(insert_query, (flag, url))
                spider.conn.commit()
        except Exception as e:
            spider.conn.rollback()
            logging.error(f"Update crawl record to database failed！ Please Check: {e}")
