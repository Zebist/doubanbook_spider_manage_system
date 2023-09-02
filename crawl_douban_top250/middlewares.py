# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import re
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

        self.logger = logging.getLogger(__name__)
        self.proxy_url = settings["PROXY_URL"]
        self.proxy_node = None
        self.proxy_list = []
        self.max_use_count = 100

    def process_request(self, request, spider):
        # 在发出请求前对请求进行处理，添加和维护proxy
        if not self.proxy_url:  # 未设置代理url，视为不启用代理，不进行处理
            return
        self.handle_request_proxy(request)  # 处理proxy
        self.handle_proxy_remain()  # 更新proxy节点的可用次数
        self.logger.info(f"\nStarting Request for URL: {request.url}, META: {request.meta}\n")

    def process_response(self, request, response, spider):
        # 处理响应时，检查是否需要切换代理并重新请求
        # 当前仅top250页面需要作重定向处理，其他页面可根据后续需要调整
        if 'top250' in request.url:
            with open(f'temp/response.html', 'w') as f:
                f.write(response.text)
            is_redirect = self.check_is_redirect(response)
            # 遇到302响应时（包括js脚本跳转）切换代理并重新请求
            if is_redirect:
                return self.handle_redirect(request, response, spider)

        return response

    def process_exception(self, request, exception, spider):
        # 异常时重新请求
        if 'proxy' in request.meta:
            res = self.retry_request_page_with_new_proxy(request, f"Exception:{exception}", spider)
            self.logger.info(
                f"\nCatch exception: {exception} when request URL: {request.url}. "
                f"Switching to a new proxy: {request.meta.get('proxy')} \n")

            return res

    def handle_redirect(self, request, response, spider):
        # 处理重定向响应
        # 设置代理
        if 'proxy' in request.meta:
            res = self.retry_request_page_with_new_proxy(request, "302 Redirecting response", spider)
            self.logger.info(
                f"\nReceived {response.status} response: {response} "
                f"Switching to a new proxy: {request.meta.get('proxy')},  "
                f"URL: {request.url} \n"
            )
            if res:
                return res
            else:
                raise IgnoreRequest("This request is being ignored because it exceeded the maximum retry limit.")

    def check_is_redirect(self, response):
        """
        检查是否重定向
        :param response: 响应对象
        :return: True是重定向 False不是重定向
        """
        # 有下一页，就视为非重定向，没有就视为重定向
        not_redirect = bool(response.css("span.next"))
        return not not_redirect
        # page_html = response.text
        # retry_flag = 'window.location.href="https://sec.douban.com/a?c=e8aaea&d="+d+"&r=https%3A%2F%2Fbook.douban.com%2Ftop250%3Fstart%3D150&k=3TDUhdqDEeE0h2MJPjIJJYlwZupXlc0IVI%2BbiEkrxYY"'
        # is_redirect = response.status == 302
        # return bool(is_redirect or re.match(r'^<script>.*</script>', page_html) or retry_flag in page_html)


    def extend_proxy_list(self, proxy_data_list):
        # 将请求到的代理列表格式化后保存
        for proxy_ob in proxy_data_list['data']:
            pn = ProxyNode(proxy_ob['ip'], proxy_ob['port'], self.max_use_count)
            self.proxy_list.append(pn)

    def refresh_proxy_list(self, proxy_url):
        # 当无可用代理时，刷新代理列表
        if not self.proxy_list:
            response = requests.get(proxy_url)
            json_data = response.json()
            try:
                if json_data['code'] == 1:
                    self.extend_proxy_list(json_data)
                else:
                    self.logger.warning(
                        f'Can not to retrieve proxy data. Status code: {response.status_code}, data: {json_data}')
            except requests.exceptions.RequestException as e:
                self.logger.error(f'An error occurred during the request of proxy: {e}')
            except AttributeError as e:
                self.logger.error(f'Attribute error: {e}')
            except Exception as e:
                self.logger.error(f'An unexpected error occurred: {e}')

    def set_proxy(self, request):
        # 设置代理
        if self.proxy_list:
            p_node = self.proxy_list.pop()
            request.meta['proxy'] = p_node.address
            self.proxy_node = p_node
            self.logger.info(f"\nGet new proxy: {request.meta['proxy']} for url: {request.url}\n")

    def update_proxy(self, request):
        # 更新代理
        self.refresh_proxy_list(self.proxy_url)  # 无可用代理时重新获取代理
        self.set_proxy(request)  # 取出代理节点并设置代理到请求中

    def use_origin_proxy(self, request):
        # 继续使用原来的proxy
        request.meta['proxy'] = self.proxy_node.address
        self.logger.info(f"\nUse proxy: {request.meta['proxy']} for url: {request.url}\n")

    def handle_proxy_remain(self):
        # 每次请求将节点可用次数减1，防止超过限制数量，防止屏蔽
        if self.proxy_node and self.proxy_node.remain_count > 0:
            self.proxy_node.remain_count -= 1

    def retry_request_page_with_new_proxy(self, request, reason, spider):
        # 启用了代理，且可用代理列表为空时，刷新代理列表
        self.update_proxy(request)  # 更新代理
        res = self._retry(request, reason=reason, spider=spider)  # 重新请求
        return res

    def handle_request_proxy(self, request):
        """
        处理请求时的proxy
        :param request: request请求对象
        :return:
        """
        # reqeust没有proxy时，进行设置处理
        if 'proxy' not in request.meta:
            # 如果存在有可用次数的代理节点，则直接使用原代理
            if self.proxy_node and self.proxy_node.remain_count != 0:
                self.use_origin_proxy(request)
            # 如果不存在，则获取新的代理
            else:
                self.update_proxy(request)  # 更新代理


class CrawlRecordMiddleware(RetryMiddleware):
    # 爬取记录中间件，用来记录url的爬取结果
    def __init__(self, *args, **kwargs):
        super(CrawlRecordMiddleware, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

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
        url = request.url
        # 只需要记录top250的页面
        if 'top250' in url:
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
            self.logger.error(f"Add crawl record to database failed！ Please Check: {e}")

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
            self.logger.error(f"Update crawl record to database failed！ Please Check: {e}")
