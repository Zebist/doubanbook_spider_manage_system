import re
from datetime import datetime

import scrapy
import psycopg2

from crawl_douban_top250.items import DoubanBookItem
from crawl_douban_top250.scrapy_headers import HEADERS


class DoubanBookSpider(scrapy.Spider):
    # 豆瓣爬虫，用于爬取豆瓣阅读TOP250
    name = "douban_book"
    start_urls = ["https://book.douban.com/top250"]

    default_meta = {
        'handle_httpstatus_list': [302],
        'dont_redirect': True,
    }

    def init_urls(self):
        # 初始化url列表，将数据库记录未成功爬取的加入到列表中
        conn = getattr(self, "conn")
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url FROM douban_books_doubanbookcrawlrecord WHERE is_ok IS NOT TRUE;
            """)
            url_list = list(map(lambda r: r[0], cursor.fetchall()))
            self.start_urls = list(set(self.start_urls + url_list))

    def start_requests(self):
        self.init_urls()  # 初始化url列表，将数据库记录的之前爬取失败的记录添加进来
        for url in self.start_urls:
            yield scrapy.Request(url, headers=HEADERS, callback=self.parse, meta=self.default_meta)

    def parse(self, response):
        self.logger.info(f'\n=============URL: {response.request.url}=============\n')
        node_list = response.css("tr.item")  # 获取本页每个书本的元素
        next_page = response.css("span.next a")  # 下一页
        for node in node_list:
            item = DoubanBookItem()  # 定义item
            title_box = self.get_title_box(node)  # 标题div
            title_a_tag = self.get_a_tag(title_box)  # 获取主标题的a标签
            title_list = self.get_title_list(title_a_tag)  # 获取标题内容
            author, publisher, date, price, base_info_raw = self.get_base_info(node)  # 获取作者、出版社、时间、价格信息、原始基础信息
            rating_box = self.get_rating_box(node)  # 评价标签

            # 构造item
            item["title"] = self.get_title(title_list)  # 清洗标题数据
            item["title_2"] = self.get_title_2(title_box)  # 第二标题
            item["cover_path"] = self.get_cover_path(node)  # 图片路径
            item["book_url"] = self.get_book_url(title_a_tag)  # 书本url
            item["base_info"] = base_info_raw  # 原始的基础信息
            item["author"] = author
            item["publisher"] = publisher
            item["publish_date"] = date
            item["price"] = self.get_num_from_text(price)  # 提取数字
            item["rating"] = self.get_rating_num(rating_box)  # 评分
            item["review_count"] = self.get_rating_count(rating_box)  # 评论人数
            item["summary"] = self.get_summary(node)  # 简介
            item["is_readability"] = self.get_is_readability(title_box)  # 判断是否可试读
            yield item

        # 请求下一页
        yield from response.follow_all(next_page, headers=HEADERS, callback=self.parse, meta=self.default_meta)

    def get_title(self, title_raw_list):
        """
        处理title字符串，拼接成可供展示的形式
        :param title_raw_list: 提取到的原标题列表
        :return: 字符串：处理后可供展示的标题
        """
        return "".join(map(lambda r: r.strip(), title_raw_list))

    def get_is_readability(self, node):
        """
        判断是否可试读
        :param node: 祖先节点
        :return: 布尔值：True可试读 or False不可试读
        """
        return bool(node.css("img[alt='可试读']").get())

    def get_base_info(self, node):
        """
        获取基础信息，并拆分成：作者、出版社、出版时间、价格
        :param node: 祖先节点
        :return: map对象： 作者、出版社、出版时间、价格、原始基础信息
        """
        # 1. 根据页面规律，按“/”分割，后三个值分别为出版社、出版时间、价格，
        # 2. 而作者可能有多个，所以我们先拆后面3个，再把前面剩下的数据都视为作者
        # 3. 再进行拼接处理
        base_info_raw = self.extract_with_node(node.css("p.pl::text"))
        *author_list, publisher, publish_date, price = base_info_raw.split('/')
        author = self.get_author(author_list)

        return map(lambda r: r.strip(), [author, publisher, publish_date, price, base_info_raw])

    def get_author(self, author_list):
        """
        将作者列表的空格清除，并用“ / ”拼接成字符串
        :param author_list: 作者列表
        :return: 字符串： 拼接后的作者信息
        """
        return " / ".join(map(lambda r: r.strip(), author_list))

    def get_num_from_text(self, text):
        """
        提取文本中的数字
        :param text: 原始文本数据
        :return: 字符串： 从文本中提取出的数字字符串; 空值： 如提取不到返回空
        """
        pattern = re.compile(r'\d+\..*\d+')
        res = re.match(pattern, text)
        return res.group() if res else res

    def get_title_box(self, node):
        """
        取出标题div
        :param node:
        :return:
        """
        return node.css("div.pl2")

    def get_a_tag(self, node):
        """
        取出标题的a标签
        :param node:
        :return:
        """
        return node.css("a")

    def get_title_list(self, node):
        """
        取出标题内容
        :param node:
        :return:
        """
        # 有可能有子标题，用getall
        return node.css("::text").getall()

    def extract_with_node(self, node):
        return node.get(default="").strip()

    def get_title_2(self, node):
        """
        取出第二标题（翻译标题）
        :param node:
        :return:
        """
        return self.extract_with_node(node.css("br + span::text"))

    def get_cover_path(self, node):
        """
        取出图片路径
        :param node:
        :return:
        """
        return node.css("a.nbg img::attr('src')").get()

    def get_book_url(self, node):
        """
        取出书本的url连接
        :param node:
        :return:
        """
        return node.css("::attr('href')").get()

    def get_rating_box(self, node):
        """
        获取评价标签
        :param node:
        :return:
        """
        return node.css("div.star")

    def get_rating_num(self, node):
        """
        获取评分
        :param node:
        :return:
        """
        return node.css("span.rating_nums::text").get()

    def get_rating_count(self, node):
        """
        获取评论人数,提取数值
        :param node:
        :return:
        """
        return node.xpath("span[@class='pl']/text()").re_first(r"\d+")
    
    def get_summary(self, node):
        """
        获取简介
        :param node: 
        :return: 
        """
        return self.extract_with_node(node.css("p.quote span.inq::text"))
