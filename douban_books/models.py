from django.db import models


class DoubanBooks(models.Model):
    """
    豆瓣阅读
    """
    title = models.CharField(max_length=255, verbose_name="书名", null=False, blank=False)
    douban_id = models.CharField(max_length=255, verbose_name="豆瓣书籍ID", null=False, blank=False, unique=True)
    title_2 = models.CharField(max_length=255, verbose_name="辅助书名", null=True)
    cover_path = models.ImageField(upload_to='images/douban_books/cover_path', max_length=255, verbose_name="封面", null=True)
    book_url = models.CharField(max_length=255, verbose_name="书籍链接", null=True)
    base_info = models.CharField(max_length=255, verbose_name="基本", null=True)
    author = models.CharField(max_length=100, verbose_name="作者", null=True)
    publisher = models.CharField(max_length=100, verbose_name="出版商", null=True)
    publish_date = models.CharField(max_length=100, verbose_name="日期", null=True)
    price = models.DecimalField(verbose_name="价格", max_digits=10, decimal_places=2, null=True)
    rating = models.FloatField(verbose_name="评分", null=True)
    review_count = models.IntegerField(verbose_name="评论人数", null=True)
    summary = models.TextField(verbose_name="简介", null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=False, blank=False)
    update_date = models.DateTimeField(verbose_name="更新时间", auto_now=True, null=False, blank=False)
    is_readability = models.BooleanField(verbose_name="可试读", null=True)

    def __str__(self):
        return self.title


class DoubanBookCrawlRecord(models.Model):
    """
    豆瓣阅读爬取记录，记录URL和爬取结果
    """
    url = models.CharField(max_length=255, unique=True, null=False, blank=False)
    is_ok = models.BooleanField(default=False)

