from rest_framework.views import APIView
from rest_framework.response import Response

from .tasks import run_spider


class SpiderCenter(APIView):
    def post(self, request):
        # 在视图中触发 Celery 任务
        run_spider.delay()
        # 返回成功响应
        return Response({"code": "success", "message": "任务已触发，请稍后检查执行结果。"})
