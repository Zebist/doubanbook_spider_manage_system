# Generated by Django 4.2.4 on 2023-09-02 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('douban_books', '0004_doubanbookcrawlrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doubanbooks',
            name='title',
            field=models.CharField(max_length=255, verbose_name='封面'),
        ),
    ]
