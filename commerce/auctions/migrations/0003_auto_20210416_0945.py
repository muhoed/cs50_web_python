# Generated by Django 3.1.7 on 2021-04-16 07:45

import auctions.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_answer_bid_category_comment_image_listing_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='image_url',
            field=models.URLField(blank=True, null=True, verbose_name="URL of product's image"),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=auctions.models.get_product_image_filename, verbose_name="Product's image"),
        ),
    ]
