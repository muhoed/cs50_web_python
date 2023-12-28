# Generated by Django 4.1.4 on 2023-12-28 21:23

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wgapi', '0002_purchase_remove_config_auto_generate_shopping_plan_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='current_stock',
        ),
        migrations.RemoveField(
            model_name='stockitem',
            name='initial_volume',
        ),
        migrations.AddField(
            model_name='config',
            name='gen_shop_plan_on_min_stock',
            field=models.BooleanField(db_column='Conf_Gen_ShopPlan_MinStock', default=False),
        ),
        migrations.AddField(
            model_name='cookingplan',
            name='note',
            field=models.TextField(blank=True, db_column='CookPlan_Note', max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name='purchase',
            name='note',
            field=models.TextField(blank=True, db_column='Purchase_Note', max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name='purchase',
            name='type',
            field=models.IntegerField(choices=[(0, 'Purchase'), (1, 'Balance entry / correction')], db_column='Purchase_Type', default=0),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='product',
            field=models.ForeignKey(db_column='PurchItem_Product', on_delete=django.db.models.deletion.RESTRICT, to='wgapi.product'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='purchase',
            field=models.ForeignKey(db_column='PurchItem_Purchase', db_index=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='wgapi.purchase'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='status',
            field=models.IntegerField(choices=[(0, 'bougth'), (1, 'partially stored'), (2, 'stored'), (3, 'moved')], db_column='PurchItem_Status', db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='status',
            field=models.IntegerField(choices=[(0, 'Active'), (1, 'Expired'), (2, 'Not placed')], db_column='StkItem_Status', default=0),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='use_till',
            field=models.DateField(db_column='StkItem_Use_Till_Date', db_index=True, default=datetime.datetime(2024, 1, 4, 22, 23, 5, 693258)),
        ),
        migrations.CreateModel(
            name='Consumption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_column='Consumption_Date', db_index=True)),
                ('type', models.IntegerField(choices=[(0, 'Cooked'), (1, 'Trashed'), (2, 'Other')], db_column='Consumption_Type', default=0)),
                ('unit', models.IntegerField(choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle'), (12, 'Cup'), (13, 'Spoon'), (14, 'Teaspoon')], db_column='Consumption_Unit')),
                ('quantity', models.FloatField(db_column='Consumption_Quantity')),
                ('note', models.TextField(blank=True, db_column='Consumption_Note', max_length=5000, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='Consumption_Created_On', db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='Consumption_Updated_On')),
                ('cooking_plan', models.ForeignKey(blank=True, db_column='Consumption_CookingPlan', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wgapi.cookingplan')),
                ('created_by', models.ForeignKey(db_column='Consumption_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(db_column='Consumption_Product', on_delete=django.db.models.deletion.RESTRICT, to='wgapi.product')),
                ('recipe_product', models.ForeignKey(blank=True, db_column='Consumption_RecipeProduct', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wgapi.recipeproduct')),
                ('stock_items', models.ManyToManyField(blank=True, null=True, to='wgapi.stockitem')),
            ],
        ),
    ]
