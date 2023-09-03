# Scrapy settings for crawl_douban_top250 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import sys
import django


sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'scrapy_management_system.settings'
django.setup()

BOT_NAME = "crawl_douban_top250"

SPIDER_MODULES = ["crawl_douban_top250.spiders"]
NEWSPIDER_MODULE = "crawl_douban_top250.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "crawl_douban_top250 (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2  # 平均下载延迟为2秒
DOWNLOAD_DELAY_RANDOMIZE = True  # 随机化下载延迟
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "crawl_douban_top250.middlewares.CrawlDoubanTop250SpiderMiddleware": 543,
#}
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "crawl_douban_top250.middlewares.ProxyMiddleware": 543,
   "crawl_douban_top250.middlewares.CrawlRecordMiddleware": 600,
}
PROXY_URL1 = "http://proxy.siyetian.com/apis_get.html?token=AesJWLORUQw4ERJdXTq10dPRVQ45kaBBjTB1STqFUeNpXQ10ERFpXT6VVMPRUV31EVVFzTUdmM.QN3UTM4UzM5YTM&limit=20&type=0&time=&repeat=0&isp=0&data_format=json"
PROXY_URL2 = "http://proxy.siyetian.com/apis_get.html?token=AesJWLNR1Zx0ERJdXTq10dPRVQ45ERFFTTB1STqFUeNpXQ10ERFpXT6VVMPRUV31EVVFzTUdmM.gNzkjM0YzM5YTM&limit=2&type=0&time=&repeat=0&isp=0&data_format=json"
PROXY_URL = PROXY_URL2

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "crawl_douban_top250.pipelines.DuplicatesPipeline": 100,  # item去重
    "crawl_douban_top250.pipelines.ImagePipeline": 200,  # 图片下载
    "crawl_douban_top250.pipelines.PostgreSQLPipeline": 300,  # 写入postgresql数据库
}
IMAGES_STORE = 'media/'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

RETRY_ENABLED = True
RETRY_TIMES = 3

# LOG_LEVEL = 'INFO'
