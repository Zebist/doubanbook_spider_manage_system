from rest_framework import serializers

from .models import DoubanBooks

class DoubanBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubanBooks
        fields = (
            'id',
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
            'update_date'
        )
