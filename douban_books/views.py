import logging

from django.shortcuts import render
from django.views.generic import View
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from .models import DoubanBooks
from .serializers import DoubanBookSerializer
from .pagination import GenericPagination, MAX_PAGE_SIZE


logger = logging.getLogger(__name__)


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
    ordering = 'id'
    search_fields = ['title', 'title_2', 'author', 'publisher']  # 搜索字段
    filter_backends = [OrderingFilter, SearchFilter]  # 过滤器

    def create(self, request, *args, **kwargs):
        try:
            # 创建记录
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            if 'unique' in str(e) and 'douban_id' in str(e):
                # 提取唯一键信息，这里假设键名为 'douban_id'
                errors_msg = self.get_error_msg(f"豆瓣书籍ID重复,请重新输入")
                return Response(errors_msg, status=status.HTTP_200_OK)
            raise IntegrityError(e)

    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except DoubanBooks.DoesNotExist:
            # 对象不存在
            errors_msg = self.get_error_msg('对象不存在')
            return Response(errors_msg, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['max_size'] = MAX_PAGE_SIZE  # 每页最大数量

        return response

    def get_error_msg(self, msg, many=False):
        e_msg = {
            'code': 'error',
        }
        if many:
            e_msg.update({'errors': msg})
        else:
            e_msg.update({'error': msg})

        return e_msg

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            # 捕获ValidationError,构造自定义错误响应
            error_msg = self.get_error_msg(exc.detail, many=True)
            return Response(error_msg, status=status.HTTP_200_OK)
        
        return super().handle_exception(exc)
