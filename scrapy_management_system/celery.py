# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置默认的 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scrapy_management_system.settings')

# 创建一个 Celery 实例
app = Celery('scrapy_management_system')

# 使用配置文件来配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的 Django app 中加载任务
app.autodiscover_tasks()
