# Generated by Django 5.0.7 on 2024-07-18 05:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplaceservice', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ozon',
            old_name='id',
            new_name='uuid',
        ),
        migrations.RenameField(
            model_name='wildberries',
            old_name='id',
            new_name='uuid',
        ),
        migrations.RenameField(
            model_name='yandexmarket',
            old_name='id',
            new_name='uuid',
        ),
    ]
