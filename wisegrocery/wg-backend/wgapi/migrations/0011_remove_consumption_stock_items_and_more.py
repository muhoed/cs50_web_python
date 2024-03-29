# Generated by Django 4.1.4 on 2024-01-23 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgapi', '0010_alter_consumption_quantity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumption',
            name='stock_items',
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='status',
            field=models.IntegerField(choices=[(0, 'Active'), (1, 'Expired'), (2, 'Not placed'), (3, 'Trashed')], db_column='StkItem_Status', default=0),
        ),
    ]
