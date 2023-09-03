from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination


class GenericPagination(PageNumberPagination):
    page_size = 10  # 每页数量
    page_size_query_param = 'size'  # URL参数设置
    page_query_param = 'page'
    max_page_size = 100  # 每页的最大数量


