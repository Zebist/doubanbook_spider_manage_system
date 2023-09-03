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
from .pagination import GenericPagination


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
    search_fields = ['title', 'title_2', 'author', 'publisher']  # 搜索字段
    filter_backends = [OrderingFilter, SearchFilter]  # 过滤器

    def create(self, request, *args, **kwargs):
        try:
            # 创建记录
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                errors = serializer.errors
                return Response(errors, status=status.HTTP_200_OK)
        except IntegrityError as e:
            if 'unique' in str(e) and 'douban_id' in str(e):
                # 提取唯一键信息，这里假设键名为 'douban_id'
                return Response({"data": f"豆瓣书籍ID重复,请重新输入"}, status=status.HTTP_200_OK)
            return self.raise_unexpected_message(e)
        except Exception as e:
            # 异常处理
            return self.raise_unexpected_message(e)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({'status': 'success', 'message': '更新成功'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            # 验证异常处理
            return Response(serializer.errors, status=status.HTTP_200_OK)
        except Exception as e:
            # 其他异常处理
            return self.raise_unexpected_message(e)

    def raise_unexpected_message(self, e):
        # 处理其他错误，记录日志
        logger.error(f"Got a unexpected error: {e}")
        return Response({'status': 'error', 'message': 'An integrity error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
