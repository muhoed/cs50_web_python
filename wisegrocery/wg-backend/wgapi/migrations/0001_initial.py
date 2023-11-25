# Generated by Django 4.1.4 on 2022-12-29 20:08

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import wgapi.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='WiseGroceryUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_column='Eq_Name', db_index=True, max_length=20, unique=True)),
                ('description', models.TextField(blank=True, db_column='Eq_Description', max_length=50, null=True)),
                ('icon', models.TextField(choices=[('freezer', 'Freezer'), ('fridge', 'Fridge'), ('buffet', 'Buffet'), ('cupboard', 'Cupboard')], db_column='Eq_Icon', default='fridge')),
                ('height', models.FloatField(blank=True, db_column='Eq_Height', help_text='Inner height, cm', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('width', models.FloatField(blank=True, db_column='Eq_Width', help_text='Inner width, cm', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('depth', models.FloatField(blank=True, db_column='Eq_Depth', help_text='Inner depth, cm', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('volume', models.FloatField(blank=True, db_column='Eq_Volume', help_text='Volume, liters', null=True)),
                ('rated_size', models.FloatField(db_column='Eq_Rated_Size', default=0.85)),
                ('free_space', models.FloatField(blank=True, db_column='Eq_Free_Space', null=True)),
                ('min_tempreture', models.FloatField(blank=True, db_column='Eq_Min_Temp', help_text='Minimal tempreture', null=True)),
                ('max_tempreture', models.FloatField(blank=True, db_column='Eq_Max_Temp', help_text='Maximum tempreture', null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='Eq_Created_On')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='Eq_Updated_On')),
                ('created_by', models.ForeignKey(db_column='Eq_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_column='Prod_Name', db_index=True, max_length=50, unique=True)),
                ('description', models.TextField(blank=True, db_column='Prod_Description', max_length=100, null=True)),
                ('category', models.IntegerField(choices=[(1, 'Fruits'), (2, 'Vegetables'), (3, 'Dairy'), (4, 'Baked goods'), (5, 'Meat'), (6, 'Fish'), (7, 'Meat alternatives'), (8, 'Cans and Jars'), (9, 'Pasta, rice, cereals'), (10, 'Sauces and Condiments'), (11, 'Herbs and Spices'), (12, 'Frozen foods'), (13, 'Snacks'), (14, 'Drinks'), (15, 'Household and Cleaning'), (16, 'Personal care'), (17, 'Pet care'), (18, 'Baby products'), (19, 'Other')], db_column='Prod_Category')),
                ('supplier', models.CharField(blank=True, db_column='Prod_Supplier', max_length=50, null=True)),
                ('picture', models.ImageField(db_column='Prod_Picture', upload_to=wgapi.models.get_icon_upload_path)),
                ('minimal_stock_volume', models.FloatField(blank=True, db_column='Prod_Min_Stock', help_text='Minimum amount of product to be maintained in stock.', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('unit', models.IntegerField(choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle')], db_column='Prod_Min_Unit')),
                ('current_stock', models.FloatField(blank=True, db_column='Prod_Current_Stock', null=True)),
                ('min_tempreture', models.FloatField(db_column='Prod_Min_Temp', help_text='Minimal storing tempreture')),
                ('max_tempreture', models.FloatField(db_column='Prod_Max_Temp', help_text='Maximum storing tempreture')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='Prod_Created_On')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='Prod_Updated_On')),
                ('alternative_to', models.ForeignKey(blank=True, db_column='Prod_Alternative', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replacement_products', to='wgapi.product')),
                ('created_by', models.ForeignKey(db_column='Prod_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_column='Rcp_Name', db_index=True, max_length=50)),
                ('description', models.TextField(db_column='Rcp_Description', max_length=1000)),
                ('num_persons', models.IntegerField(db_column='Rcp_Output_Portions', validators=[django.core.validators.MinValueValidator(0)])),
                ('cooking_time', models.DurationField(db_column='Rcp_Cook_Time')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='Rcp_Created_On')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='Rcp_Updated_On')),
                ('created_by', models.ForeignKey(db_column='Rcp_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.IntegerField(choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle')], db_column='StkItem_Unit')),
                ('volume', models.FloatField(db_column='StkItem_Volume')),
                ('initial_volume', models.FloatField(blank=True, db_column='StkItem_Init_Volume', null=True)),
                ('use_till', models.DateField(db_column='StkItem_Use_Till_Date', db_index=True, default=datetime.datetime(2023, 1, 5, 21, 8, 32, 152563))),
                ('status', models.IntegerField(choices=[(0, 'Active'), (1, 'Cooked'), (2, 'Expired'), (3, 'Wasted'), (4, 'Not placed')], db_column='StkItem_Status', default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='StkItem_Created_On')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='StkItem_Updated_On')),
                ('created_by', models.ForeignKey(db_column='StkItem_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('equipment', models.ForeignKey(db_column='StkItem_Equip', on_delete=django.db.models.deletion.CASCADE, to='wgapi.equipment')),
                ('product', models.ForeignKey(db_column='StkItem_Prod', on_delete=django.db.models.deletion.CASCADE, to='wgapi.product')),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_column='ShopPlan_Date', db_index=True)),
                ('note', models.TextField(blank=True, db_column='ShopPlan_Note', null=True)),
                ('status', models.IntegerField(choices=[(0, 'Entered'), (1, 'Fulfilled'), (3, 'Partially fulfilled'), (4, 'Closed')], db_column='ShopPlan_Status', db_index=True, default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='ShopPlan_Created_On', db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='ShopPlan_Updated_On')),
                ('created_by', models.ForeignKey(db_column='ShopPlan_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.IntegerField(choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle')], db_column='RcpProd_Unit')),
                ('volume', models.FloatField(db_column='RcpProd_Volume', validators=[django.core.validators.MinValueValidator(0)])),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='RcpProd_Created_On')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='RcpProd_Updated_On')),
                ('created_by', models.ForeignKey(db_column='RcpProd_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(db_column='RcpProd_Prod', on_delete=django.db.models.deletion.CASCADE, to='wgapi.product')),
                ('recipe', models.ForeignKey(db_column='RcpProd_Recipe', on_delete=django.db.models.deletion.CASCADE, to='wgapi.recipe')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='items',
            field=models.ManyToManyField(db_column='Rcp_Item', through='wgapi.RecipeProduct', to='wgapi.product'),
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.IntegerField(choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle')], db_column='PurchItem_Unit')),
                ('volume', models.FloatField(db_column='PurchItem_Volume', validators=[django.core.validators.MinValueValidator(0)])),
                ('status', models.IntegerField(choices=[(0, 'to buy'), (1, 'bougth'), (2, 'stored'), (3, 'moved')], db_column='PurchItem_Status', db_index=True, default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='PurchItem_Created_On', db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='PurchItem_Updated_On')),
                ('created_by', models.ForeignKey(db_column='PurchItem_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(db_column='PurchItem_Prod', on_delete=django.db.models.deletion.CASCADE, to='wgapi.product')),
                ('shop_plan', models.ForeignKey(db_column='PurchItem_Shop_Plan', on_delete=django.db.models.deletion.CASCADE, to='wgapi.shoppingplan')),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_column='EqType_Name', db_index=True, max_length=20, unique=True)),
                ('description', models.TextField(blank=True, db_column='EqType_Description', max_length=50, null=True)),
                ('base_type', models.CharField(choices=[('FRE', 'Freezer'), ('FRD', 'Fridge'), ('BFT', 'Buffet'), ('CBD', 'Cupboard')], db_column='EqType_Base_Type', default='CBD', help_text='Equipment base type', max_length=3)),
                ('min_temp', models.FloatField(blank=True, db_column='EqType_Min_Temp', help_text='Minimal tempreture', null=True)),
                ('max_temp', models.FloatField(blank=True, db_column='EqType_Max_Temp', help_text='Maximum tempreture', null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='EqType_Created_On')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='EqType_Updated_On')),
                ('created_by', models.ForeignKey(db_column='EqType_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='equipment',
            name='type',
            field=models.ForeignKey(db_column='Eq_Type', on_delete=django.db.models.deletion.CASCADE, to='wgapi.equipmenttype'),
        ),
        migrations.CreateModel(
            name='CookingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_column='CookPlan_Date', db_index=True)),
                ('meal', models.IntegerField(choices=[(1, 'Breakfast'), (2, 'Lunch'), (3, 'Dinner')], db_column='CookPlan_Meal', db_index=True, default=1)),
                ('persons', models.IntegerField(db_column='CookPlan_Persons', validators=[django.core.validators.MinValueValidator(0)])),
                ('status', models.IntegerField(choices=[(0, 'Entered'), (1, 'Cooked')], db_column='CookPlan_Status', default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='CookPlan_Created_On')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='CookPlan_Updated_On')),
                ('created_by', models.ForeignKey(db_column='CookPlan_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('recipes', models.ManyToManyField(db_column='CookPlan_Recipe', to='wgapi.recipe')),
            ],
        ),
        migrations.CreateModel(
            name='ConversionRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_column='ConvRule_Name', max_length=50, unique=True)),
                ('description', models.TextField(blank=True, db_column='ConvRule_Description', max_length=400, null=True)),
                ('from_unit', models.IntegerField(choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle')], db_column='ConvRule_From_Unit')),
                ('to_unit', models.IntegerField(choices=[(1, 'Liter'), (2, 'Milliliter'), (3, 'Gallon'), (4, 'gram'), (5, 'kilogram'), (6, 'pound'), (7, 'ounce'), (8, 'Piece'), (9, 'Pack'), (10, 'Can'), (11, 'Bottle')], db_column='ConvRule_To_Unit')),
                ('ratio', models.FloatField(db_column='ConvRule_Ratio', help_text="Ratio of 'To unit' to 'From unit' for a product.", validators=[django.core.validators.MinValueValidator(1e-10)])),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='ConvRule_Created_On', db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='ConvRule_Updated_On')),
                ('created_by', models.ForeignKey(db_column='ConvRule_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(db_column='ConvRule_Prod', on_delete=django.db.models.deletion.CASCADE, to='wgapi.product')),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_by_email', models.BooleanField(db_column='Conf_Notify_By_Email', default=False)),
                ('notify_on_expiration', models.BooleanField(db_column='Conf_Notify_Expire', default=True)),
                ('notify_on_expiration_before', models.DurationField(blank=True, db_column='Conf_Notify_Expired_Days', null=True)),
                ('default_expired_action', models.IntegerField(choices=[(0, 'Trash'), (1, 'Allow'), (2, 'Prolong')], db_column='Conf_Default_Expired_Action', default=0)),
                ('prolong_expired_for', models.DurationField(db_column='Conf_Prolong_Expired_Days', default=datetime.timedelta(days=7))),
                ('notify_on_min_stock', models.BooleanField(db_column='Conf_Notify_Min_Stock', default=True)),
                ('nofity_on_purchase_plan_generated', models.BooleanField(db_column='Conf_Notify_Purchase_Plan_Gen', default=False)),
                ('nofity_on_shopping_plan_generated', models.BooleanField(db_column='Conf_Notify_Shop_Plan_Gen', default=False)),
                ('auto_generate_shopping_plan', models.BooleanField(db_column='Conf_Gen_Shop_Plan', default=False)),
                ('allow_replacement_use', models.BooleanField(db_column='Conf_Allow_Replacement', default=True)),
                ('gen_shop_plan_on_min_stock', models.BooleanField(db_column='Conf_Gen_ShopPlan_MinStock', default=True)),
                ('gen_shop_plan_repeatedly', models.BooleanField(db_column='Conf_Gen_ShopPlan_Repeatedly', default=True)),
                ('gen_shop_plan_period', models.DurationField(blank=True, db_column='Conf_GenShopPlan_Periodicity', null=True, validators=[django.core.validators.MinValueValidator(datetime.timedelta(days=3))])),
                ('base_shop_plan_on_historic_data', models.BooleanField(db_column='Conf_Gen_ShopPlan_Historic', default=True)),
                ('historic_period', models.DurationField(db_column='Conf_Hst_Period', default=datetime.timedelta(days=30), validators=[django.core.validators.MinValueValidator(datetime.timedelta(days=10))])),
                ('base_shop_plan_on_cook_plan', models.BooleanField(db_column='Conf_Gen_ShopPlan_CookPlan', default=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='Conf_Created_On', db_index=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='Conf_Updated_On')),
                ('created_by', models.OneToOneField(db_column='Conf_Created_By', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]