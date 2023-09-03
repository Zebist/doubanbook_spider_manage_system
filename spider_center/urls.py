from django.urls import path
from .views import SpiderCenter


urlpatterns = [
    path('', SpiderCenter.as_view()),
]

