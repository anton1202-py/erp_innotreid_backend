# Generated by Django 5.0.8 on 2024-10-07 07:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0042_alter_inventory_total_alter_inventory_total_fact_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='shipment',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='shipment',
            name='recomamand_supplier',
        ),
    ]
