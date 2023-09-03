from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # 使用默认的异常处理器获得标准响应
    response = exception_handler(exc, context)
    # 自定义响应格式
    if response is not None:
        response.data = {
            'status': 'error',
            'message': response.data['detail']  # 使用默认的错误消息
        }

    return response
