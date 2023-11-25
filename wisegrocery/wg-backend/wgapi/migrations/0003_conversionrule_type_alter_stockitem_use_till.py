# Generated by Django 4.1.4 on 2023-01-06 17:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgapi', '0002_remove_conversionrule_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversionrule',
            name='type',
            field=models.IntegerField(choices=[(0, 'Common conversion rule'), (1, 'Product specific conversion rule')], db_column='ConvRule_Type', default=0),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='use_till',
            field=models.DateField(db_column='StkItem_Use_Till_Date', db_index=True, default=datetime.datetime(2023, 1, 13, 18, 19, 6, 421256)),
        ),
    ]