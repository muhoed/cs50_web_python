# Generated by Django 4.1.4 on 2024-01-20 16:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgapi', '0007_remove_product_use_period_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='original_quantity',
            field=models.FloatField(blank=True, db_column='PurchItem_Original_Qty', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='original_unit',
            field=models.IntegerField(blank=True, choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle'), (12, 'Cup'), (13, 'Spoon'), (14, 'Teaspoon')], db_column='PurchItem_Original_Unit', null=True),
        ),
    ]
