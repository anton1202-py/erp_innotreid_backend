# Generated by Django 5.0.8 on 2024-08-26 13:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('vendor_code', models.CharField(max_length=1000)),
                ('ozon_sku', models.CharField(max_length=1000, null=True)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'db_table': 'product',
                'ordering': ('vendor_code',),
            },
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('country_name', models.CharField(max_length=200)),
                ('oblast_okrug_name', models.CharField(max_length=200)),
                ('region_name', models.CharField(max_length=200)),
                ('shelf', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Warehouse',
                'verbose_name_plural': 'Warehouse',
                'db_table': 'warehouse',
                'ordering': ['name'],
                'unique_together': {('name', 'country_name', 'oblast_okrug_name', 'region_name', 'shelf')},
            },
        ),
        migrations.CreateModel(
            name='ProductStock',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('ozon_quantity', models.IntegerField(default=0)),
                ('wildberries_quantity', models.IntegerField(default=0)),
                ('yandex_market_quantity', models.IntegerField(default=0)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_stocks', to='company.company')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='product.product')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.warehouse')),
            ],
            options={
                'verbose_name': 'Product stock',
                'verbose_name_plural': 'Product stocks',
                'db_table': 'product_stocks',
                'ordering': ('product__vendor_code',),
                'unique_together': {('product', 'company', 'warehouse')},
            },
        ),
        migrations.CreateModel(
            name='ProductSale',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateTimeField()),
                ('marketplace_type', models.CharField(choices=[('wildberries', 'Wildberries'), ('ozon', 'Ozon'), ('yandexmarket', 'YandexMarket')], max_length=50)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_sales', to='company.company')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='product.product')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.warehouse')),
            ],
            options={
                'verbose_name': 'Product sale',
                'verbose_name_plural': 'Product sales',
                'db_table': 'product_sales',
                'ordering': ('product__vendor_code',),
                'unique_together': {('product', 'company', 'date')},
            },
        ),
        migrations.CreateModel(
            name='ProductOrder',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateTimeField()),
                ('marketplace_type', models.CharField(choices=[('wildberries', 'Wildberries'), ('ozon', 'Ozon'), ('yandexmarket', 'YandexMarket')], max_length=50)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_orders', to='company.company')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='product.product')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.warehouse')),
            ],
            options={
                'verbose_name': 'Product order',
                'verbose_name_plural': 'Product orders',
                'db_table': 'product_orders',
                'ordering': ('product__vendor_code',),
                'unique_together': {('product', 'company', 'date')},
            },
        ),
    ]
