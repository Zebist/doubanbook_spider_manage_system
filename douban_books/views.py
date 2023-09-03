from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DoubanBooks
from .serializers import DoubanBookSerializer
from .pagination import GenericPagination


class IndexVIew(View):
    """
    首页
    """
    def get(self, request):
        return render(request, 'index.html')


class DoubanBookViewSet(viewsets.ModelViewSet):
    """
    豆瓣书籍接口，用于实现前端CRUD
    """
    queryset = DoubanBooks.objects.all()  # 查询集
    serializer_class = DoubanBookSerializer  # 序列化器
    pagination_class = GenericPagination  # 分页器
    ordering_fields = '__all__'  # 排序字段
    search_fields = ['title', 'title_2', 'author', 'publisher']  # 搜索字段
    filter_backends = [OrderingFilter, SearchFilter]  # 过滤器

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     page = self.paginate_queryset(queryset)  # 使用 DRF 的分页方法
    #
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         # 在响应数据中添加当前页码和每页数量
    #         custom_data = {
    #             'current_page': self.paginator.page.number,
    #             'page_size': self.paginator.page.paginator.per_page,
    #             'results': serializer.data,
    #         }
    #         return self.get_paginated_response(custom_data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


