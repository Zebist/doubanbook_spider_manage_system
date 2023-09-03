import logging

from django.shortcuts import render
from django.views.generic import View
from django.db import IntegrityError
from django.conf.global_settings import MEDIA_URL
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

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
        except Exception as e:
            # 异常处理
            return self.raise_unexpected_message(e)

    # def get_image_path(self, request):
    #     """
    #     获取图片路径
    #     :param request: 请求对象
    #     :return: 图片路径
    #     """
    #     return self._handle_image(request)

    # def _handle_image(self, request):
    #     """
    #     处理图片，将图片保存到指定位置，将路径保存到数据库
    #     :param request: 请求对象
    #     :return:
    #     """
    #     image = request.data.get('cover_image')
    #     if not image:  # 未上传图片
    #         return
    #     image_path_root = f'{MEDIA_URL}images/douban_books/'  # 设置保存路径
    #     print(dir(image))
    #     image_path = f'cover_path/{image.name}'  # 设置保存路径
    #     image_path = f"{image_path_root}{image_path}"
    #     try:
    #         with open(image_path, 'wb') as f:
    #             for chunk in image.chunks():
    #                 f.write(chunk)
    #     except FileNotFoundError:
    #         # 处理文件不存在异常
    #         logger.error(f"File:{image_path} Not Found!")
    #     except PermissionError:
    #         # 处理文件无法写入异常
    #         logger.error(f'Permission Denied When writting to file:{image_path}!')
    #     except Exception as e:
    #         # 处理其他异常
    #         logger.error(f'Got a unexpected Exception:{e}, File:{image_path}')
    #     finally:
    #         return image_path

    def raise_unexpected_message(self, e):
        # 处理其他错误，记录日志
        logger.error(f"Got a unexpected error: {e}")
        return Response({'status': 'error', 'message': 'An integrity error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
