from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    # 使用默认的异常处理器获得标准响应
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        # 自定义 ValidationError 的处理逻辑
        if response is not None:
            response.data = {
                'status': 'error',
                'message': response.data['detail'],
                'details': response.data
            }

    return response
