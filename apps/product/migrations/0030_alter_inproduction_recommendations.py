# Generated by Django 5.0.8 on 2024-09-22 07:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_product_barcode_product_marketplace_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inproduction',
            name='recommendations',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.recommendations'),
        ),
    ]
