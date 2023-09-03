from rest_framework import serializers

from .models import DoubanBooks

class DoubanBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubanBooks
        fields = (
            'id',
            'douban_id',
            'cover_path',
            'title',
            'title_2',
            'is_readability',
            'book_url',
            'author',
            'publisher',
            'publish_date',
            'price',
            'rating',
            'review_count',
            'summary',
            'create_date',
            'update_date',
        )

    cover_path = serializers.ImageField(
        max_length=None, use_url=True, label='封面'
    )

    title = serializers.CharField(
        label='书名',
        max_length=255,
        error_messages={
            'required': '书名是必填字段。',
            'blank': '书名是必填字段。',
            'max_length': '书名不能超过255个字符。',
        }
    )
    douban_id = serializers.CharField(
        label='豆瓣 id',
        max_length=255,
        error_messages={
            'required': '豆瓣ID是必填字段。',
            'blank': '豆瓣ID是必填字段。',
            'max_length': '姓名不能超过100个字符。',
            'unique': '豆瓣ID不能重复',
        }
    )

    def validate_rating(self, value):
        # 验证评分是否在1～10之间
        if value and (value > 10 or value < 1):
            raise serializers.ValidationError(f"评分必须在1～10之间，请重新输入！")

        return value

    def validate_douban_id(self, value):
        # 验证字段唯一性
        if DoubanBooks.objects.filter(douban_id=value).exists():
            raise serializers.ValidationError(f"豆瓣ID： {value} 已存在，请重新输入！")

        return value

