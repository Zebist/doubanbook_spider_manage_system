import random

from urllib.parse import urlparse

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
]

HEADERS = {
    "Host": "book.douban.com",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": random.choice(USER_AGENT_LIST),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    'Referer': 'no-referrer-when-downgrade',
    # "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    # "Cookie": "bid=-76L2a3ry_8; __utmc=30149280; __utmz=30149280.1693659729.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=81379588; ap_v=0,6.0; __utma=30149280.1125376481.1693659729.1693659729.1693669069.2; __utmb=30149280.2.10.1693669069; __utma=81379588.1772479821.1693659729.1693659729.1693669085.2; __utmz=81379588.1693669085.2.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/misc/sorry; __utmb=81379588.1.10.1693669085; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1693669085%2C%22https%3A%2F%2Fwww.douban.com%2Fmisc%2Fsorry%3Foriginal-url%3Dhttps%253A%252F%252Fbook.douban.com%252Ftop250%253Fstart%253D150%22%5D; _pk_id.100001.3ac3=b44b60f31d7b86c4.1693659729.2.1693669085.1693659769.; _pk_ses.100001.3ac3=*"
}


def get_image_headers(url):
    parsed_url = urlparse(url)
    image_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-encoding": "gzip, deflate, br",
        "Accept-language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": parsed_url.netloc,
        # "cache-control": "no-cache",
        # "pragma": "no-cache",
        "Sec-fetch-dest": "document",
        "Sec-fetch-mode": "navigate",
        "Sec-fetch-site": "none",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": random.choice(USER_AGENT_LIST),
    }
    return image_headers
