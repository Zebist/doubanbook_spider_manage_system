from django.contrib import admin
from django.urls import path, include
from .views import IndexVIew

urlpatterns = [
    path('/index/', IndexVIew.as_view()),
    path('', IndexVIew.as_view()),
]
