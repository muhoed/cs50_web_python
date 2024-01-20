# Generated by Django 4.1.4 on 2024-01-20 22:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgapi', '0009_remove_purchaseitem_original_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumption',
            name='quantity',
            field=models.DecimalField(db_column='Consumption_Quantity', decimal_places=2, max_digits=9),
        ),
        migrations.AlterField(
            model_name='conversionrule',
            name='ratio',
            field=models.DecimalField(db_column='ConvRule_Ratio', decimal_places=9, help_text="Ratio of 'To unit' to 'From unit' for a product.", max_digits=15, validators=[django.core.validators.MinValueValidator(1e-10)]),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='free_space',
            field=models.DecimalField(blank=True, db_column='Eq_Free_Space', decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='volume',
            field=models.DecimalField(blank=True, db_column='Eq_Volume', decimal_places=2, help_text='Volume, liters', max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='minimal_stock_volume',
            field=models.DecimalField(blank=True, db_column='Prod_Min_Stock', decimal_places=2, help_text='Minimum amount of product to be maintained in stock.', max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='quantity',
            field=models.DecimalField(db_column='PurchItem_Qty', decimal_places=2, max_digits=9, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='recipeproduct',
            name='volume',
            field=models.DecimalField(db_column='RcpProd_Volume', decimal_places=2, max_digits=9, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='volume',
            field=models.DecimalField(db_column='StkItem_Volume', decimal_places=2, max_digits=9),
        ),
    ]
