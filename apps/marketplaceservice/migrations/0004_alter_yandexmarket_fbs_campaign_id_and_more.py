# Generated by Django 5.0.8 on 2024-11-03 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplaceservice', '0003_remove_yandexmarket_uuid_yandexmarket_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yandexmarket',
            name='fbs_campaign_id',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='FBS Кампания ID YandexMarket'),
        ),
        migrations.AlterField(
            model_name='yandexmarket',
            name='fby_campaign_id',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='FBY Кампания ID YandexMarket'),
        ),
    ]