# Generated by Django 4.1.4 on 2023-12-17 20:21

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wgapi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_column='Purchase_Date', db_index=True)),
                ('store', models.CharField(blank=True, db_column='Purchase_Store', db_index=True, max_length=100, null=True)),
                ('total_amount', models.DecimalField(blank=True, db_column='Purchase_TotalAmount', decimal_places=2, max_digits=10, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='Purchase_Created_On', db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='Purchase_Updated_On')),
                ('created_by', models.ForeignKey(db_column='Purchase_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='config',
            name='auto_generate_shopping_plan',
        ),
        migrations.RemoveField(
            model_name='config',
            name='gen_shop_plan_on_min_stock',
        ),
        migrations.RemoveField(
            model_name='config',
            name='gen_shop_plan_period',
        ),
        migrations.RemoveField(
            model_name='config',
            name='gen_shop_plan_repeatedly',
        ),
        migrations.RemoveField(
            model_name='config',
            name='nofity_on_shopping_plan_generated',
        ),
        migrations.RemoveField(
            model_name='purchaseitem',
            name='shop_plan',
        ),
        migrations.RemoveField(
            model_name='purchaseitem',
            name='volume',
        ),
        migrations.RemoveField(
            model_name='stockitem',
            name='product',
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='price',
            field=models.DecimalField(blank=True, db_column='PurchItem_Price', decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='quantity',
            field=models.FloatField(db_column='PurchItem_Qty', default=0, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockitem',
            name='purchase_item',
            field=models.ForeignKey(db_column='StkItem_Prod', default=1, on_delete=django.db.models.deletion.CASCADE, to='wgapi.purchaseitem'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='product',
            field=models.ForeignKey(db_column='PurchItem_Product', on_delete=django.db.models.deletion.CASCADE, to='wgapi.product'),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='initial_volume',
            field=models.FloatField(db_column='StkItem_Init_Volume', default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='use_till',
            field=models.DateField(db_column='StkItem_Use_Till_Date', db_index=True, default=datetime.datetime(2023, 12, 24, 21, 20, 50, 878395)),
        ),
        migrations.DeleteModel(
            name='ShoppingPlan',
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='purchase',
            field=models.ForeignKey(blank=True, db_column='PurchItem_Purchase', null=True, on_delete=django.db.models.deletion.CASCADE, to='wgapi.purchase'),
        ),
    ]
