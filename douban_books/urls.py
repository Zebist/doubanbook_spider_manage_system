from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from douban_books.views import DoubanBookViewSet
from rest_framework.routers import DefaultRouter
from .views import IndexVIew

router = DefaultRouter()
router.register(r'api/douban_books', DoubanBookViewSet)

urlpatterns = [
    path('index/', IndexVIew.as_view()),  # 首页
    path('', IndexVIew.as_view()),  # 首页
    path('', include(router.urls)),  # 豆瓣书籍api
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
