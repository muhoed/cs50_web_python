import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from . import wg_enumeration


def get_icon_upload_path(stock_item, filename):
    instance_type = type(stock_item).__name__.lower()
    slug = slugify(stock_item.name)
    return "icons/%s/%s-%s" % (instance_type, slug, filename)

class WiseGroceryUser(AbstractUser):
	email = models.EmailField(_('email address'), unique=True, null=False, blank=False)

class EquipmentType(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False, null=False, db_column="EqType_Name", db_index=True)
    description = models.TextField(max_length=50, blank=True, null=True, db_column="EqType_Description")

    base_type = models.CharField(
        help_text=_("Equipment base type"), choices=wg_enumeration.BaseEquipmentTypes.choices, 
        default=wg_enumeration.BaseEquipmentTypes.CUPBOARD, blank=False, null=False,
        max_length=3, db_column="EqType_Base_Type")

    min_temp = models.FloatField(help_text=_("Minimal tempreture"), blank=True, null=True, db_column="EqType_Min_Temp")
    max_temp = models.FloatField(help_text=_("Maximum tempreture"), blank=True, null=True, db_column="EqType_Max_Temp")

    created_on = models.DateTimeField(auto_now_add=True, db_column="EqType_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="EqType_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="EqType_Created_By")

    def save(self, *args, **kwargs):
        if self.min_temp is None:
            self.min_temp = wg_enumeration.BASE_EQUIPMENT_TEMPS[self.base_type.value][0]
        if self.max_temp is None:
            self.max_temp = wg_enumeration.BASE_EQUIPMENT_TEMPS[self.base_type.value][1]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.description}.'


class Equipment(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False, null=False, db_column="Eq_Name", db_index=True)
    description = models.TextField(max_length=50, blank=True, null=True, db_column="Eq_Description")
    
    type = models.ForeignKey(
        EquipmentType, on_delete=models.CASCADE, blank=False, 
        null=False, db_column="Eq_Type", db_index=True
        )

    icon = models.TextField(
        choices=list(wg_enumeration.BASE_EQUIPMENT_ICONS.values()), 
        default=wg_enumeration.BASE_EQUIPMENT_ICONS[wg_enumeration.BaseEquipmentTypes.FRIDGE.value][0],
        blank=False, null=False, db_column="Eq_Icon"
        )

    height = models.FloatField(
        help_text=_("Inner height, cm"), validators=[MinValueValidator(0)], 
        blank=True, null=True, db_column="Eq_Height"
        )
    width = models.FloatField(
        help_text=_("Inner width, cm"), validators=[MinValueValidator(0)], 
        blank=True, null=True, db_column="Eq_Width"
        )
    depth = models.FloatField(
        help_text=_("Inner depth, cm"), validators=[MinValueValidator(0)], 
        blank=True, null=True, db_column="Eq_Depth"
        )

    volume = models.FloatField(help_text=_("Volume, liters"), blank=True, null=True, db_column="Eq_Volume")
    rated_size = models.FloatField(blank=False, null=False, default=0.85, db_column="Eq_Rated_Size")

    free_space = models.FloatField(blank=True, null=True, db_column="Eq_Free_Space")

    min_tempreture = models.FloatField(help_text=_("Minimal tempreture"), blank=True, null=True, db_column="Eq_Min_Temp")
    max_tempreture = models.FloatField(help_text=_("Maximum tempreture"), blank=True, null=True, db_column="Eq_Max_Temp")

    created_on = models.DateTimeField(auto_now_add=True, db_column="Eq_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="Eq_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="Eq_Created_By")

    def get_volume(self):
        if self.volume is None and self.height is not None and self.width is not None and self.depth is not None:
            return (self.height * self.width * self.depth) / 10
        return None

    def set_min_temp(self):
        return self.type.min_temp

    def set_max_temp(self):
        return self.type.max_temp

    def save(self, *args, **kwargs):
        if self.volume is None:
            self.volume = self.get_volume()
        if self.min_tempreture is None:
            self.min_tempreture = self.set_min_temp()
        if self.max_tempreture is None:
            self.max_tempreture = self.set_max_temp()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}, type: {self.type.label}, volume: {self.volume} l.'


class Product(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False, null=False, db_column="Prod_Name", db_index=True)
    description = models.TextField(max_length=100, blank=True, null=True, db_column="Prod_Description")

    category = models.IntegerField(
        choices=wg_enumeration.ProductCategories.choices, blank=False, 
        null=False, db_column="Prod_Category"
        )

    supplier = models.CharField(max_length=50, blank=True, null=True, db_column="Prod_Supplier")
    picture = models.ImageField(upload_to=get_icon_upload_path, blank=False, null=False, db_column="Prod_Picture")
    
    minimal_stock_volume = models.FloatField(
        help_text="Minimum amount of product to be maintained in stock.", validators=[MinValueValidator(0)],
        blank=True, null=True, db_column="Prod_Min_Stock"
        )
    unit = models.IntegerField(choices=wg_enumeration.VolumeUnits.choices, blank=False, null=False, db_column="Prod_Min_Unit")
    current_stock = models.FloatField(blank=True, null=True, db_column="Prod_Current_Stock")

    min_tempreture = models.FloatField(help_text=_("Minimal storing tempreture"), blank=False, null=False, db_column="Prod_Min_Temp")
    max_tempreture = models.FloatField(help_text=_("Maximum storing tempreture"), blank=False, null=False, db_column="Prod_Max_Temp")

    alternative_to = models.ForeignKey(
        'Product', related_name="replacement_products", on_delete=models.SET_NULL, 
        blank=True, null=True, db_column="Prod_Alternative"
        )

    created_on = models.DateTimeField(auto_now_add=True, db_column="Prod_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="Prod_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="Prod_Created_By")

    def save(self, *args, **kwargs):
        if self.pisture is None:
            self.picture.name = f'icons/{type(self).__name__.lower()}/{slugify(self.category.label)}.png'

    def __str__(self):
        return f'{self.name} / {self.category.label}'

class Recipe(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, db_column="Rcp_Name", db_index=True)
    description = models.TextField(max_length=1000, blank=False, null=False, db_column="Rcp_Description")
    items = models.ManyToManyField(Product, through="RecipeProduct", blank=False, db_column="Rcp_Item")
    num_persons = models.IntegerField(
        validators=[MinValueValidator(0)], blank=False, null=False, 
        db_column="Rcp_Output_Portions"
        )
    cooking_time = models.DurationField(blank=False, null=False, db_column="Rcp_Cook_Time")
    
    created_on = models.DateTimeField(auto_now_add=True, db_column="Rcp_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="Rcp_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="Rcp_Created_By")

    def __str__(self):
        return f'Recipe of {self.name} for {self.output} persons.'

class RecipeProduct(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, blank=False, 
        null=False, db_column="RcpProd_Recipe", db_index=True
        )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, null=False, 
        db_column="RcpProd_Prod", db_index=True
        )
    unit = models.IntegerField(choices=wg_enumeration.VolumeUnits.choices, blank=False, null=False, db_column="RcpProd_Unit")
    volume = models.FloatField(validators=[MinValueValidator(0)], blank=False, null=False, db_column="RcpProd_Volume")
    
    created_on = models.DateTimeField(auto_now_add=True, db_column="RcpProd_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="RcpProd_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="RcpProd_Created_By")

    def __str__(self):
        return f'{self.volume}{self.unit} of {self.product.name} required for recipe {self.recipe.name}.'

class CookingPlan(models.Model):
    date = models.DateField(blank=False, null=False, db_column="CookPlan_Date", db_index=True)
    meal = models.IntegerField(
        choices=wg_enumeration.Meals.choices, blank=False, null=False, default=wg_enumeration.Meals.BREAKFAST,
        db_column="CookPlan_Meal", db_index=True
        )
    persons = models.IntegerField(validators=[MinValueValidator(0)], blank=False, null=False, db_column="CookPlan_Persons")
    recipes = models.ManyToManyField(Recipe, blank=False, db_column="CookPlan_Recipe")
    status = models.IntegerField(
        choices=wg_enumeration.CookPlanStatuses.choices, blank=False, null=False, 
        default=wg_enumeration.CookPlanStatuses.ENTERED, db_column="CookPlan_Status"
        )
    
    created_on = models.DateTimeField(auto_now_add=True, db_column="CookPlan_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="CookPlan_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="CookPlan_Created_By")

    def __str__(self):
        return f'Cooking plan for {self.persons} on {self.date}.'

class Purchase(models.Model):
    date = models.DateField(blank=False, null=False, db_column="Purchase_Date", db_index=True)
    #shop_plan = models.ForeignKey('ShoppingPlan', on_delete=models.SET_NULL, blank=True, null=True, db_column="Purchase_ShoppingPlan")
    store = models.CharField(max_length=100, blank=True, null=True, db_column="Purchase_Store", db_index=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, db_column="Purchase_TotalAmount")

    created_on = models.DateTimeField(db_index=True, auto_now_add=True, db_column="Purchase_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="Purchase_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="Purchase_Created_By")

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, db_index=True, blank=True, null=True, db_column="PurchItem_Purchase")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True, blank=False, null=False, db_column="PurchItem_Product")
    unit = models.IntegerField(choices=wg_enumeration.VolumeUnits.choices, blank=False, null=False, db_column="PurchItem_Unit")
    quantity = models.FloatField(blank=False, null=False, validators=[MinValueValidator(0)], db_column="PurchItem_Qty")
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, validators=[MinValueValidator(0)], db_column="PurchItem_Price")
    status = models.IntegerField(
            choices=wg_enumeration.PurchaseStatuses.choices, default=wg_enumeration.PurchaseStatuses.TOBUY,
            blank=False, null=False, db_column="PurchItem_Status", db_index=True
        )
    created_on = models.DateTimeField(db_index=True, auto_now_add=True, db_column="PurchItem_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="PurchItem_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="PurchItem_Created_By")

    def __str__(self):
        return f'{self.volume}{self.unit} of {self.product.name} \
            {wg_enumeration.PurchaseStatuses.TOBUY.label if self.status == wg_enumeration.PurchaseStatuses.TOBUY else wg_enumeration.PurchaseStatuses.BOUGHT.label}.'

class StockItem(models.Model):
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, blank=False, null=False, db_column="StkItem_Prod", db_index=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=False, null=False, db_column="StkItem_Equip", db_index=True)
    unit = models.IntegerField(choices=wg_enumeration.VolumeUnits.choices, blank=False, null=False, db_column="StkItem_Unit")
    volume = models.FloatField(blank=False, null=False, db_column="StkItem_Volume")
    initial_volume = models.FloatField(blank=False, null=False, db_column="StkItem_Init_Volume")
    use_till = models.DateField(
        blank=False, null=False, default=datetime.datetime.now()+datetime.timedelta(days=7), 
        db_column="StkItem_Use_Till_Date", db_index=True
        )
    status = models.IntegerField(
        choices=wg_enumeration.STOCK_STATUSES.choices, default=wg_enumeration.STOCK_STATUSES.ACTIVE,
        blank=False, null=False, db_column="StkItem_Status"
        )

    created_on = models.DateTimeField(auto_now_add=True, db_column="StkItem_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="StkItem_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="StkItem_Created_By")

    def save(self, *args, **kwargs):
        if self.initial_volume is None:
            self.initial_volume = self.volume

    def __str__(self):
        return f'{self.volume}{self.unit} of {self.product.name} stored at {self.equipment.name}.'

# class ShoppingPlan(models.Model):
#     date = models.DateField(db_index=True, blank=False, null=False, db_column="ShopPlan_Date")
#     note = models.TextField(blank=True, null=True, db_column="ShopPlan_Note")
#     status = models.IntegerField(
#             choices=wg_enumeration.ShopPlanStatuses.choices, default=wg_enumeration.ShopPlanStatuses.ENTERED,
#             blank=False, null=False, db_column="ShopPlan_Status", db_index=True
#         )
#     created_on = models.DateTimeField(db_index=True, auto_now_add=True, db_column="ShopPlan_Created_On")
#     updated_on = models.DateTimeField(auto_now=True, db_column="ShopPlan_Updated_On")
#     created_by = models.ForeignKey(
#         WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="ShopPlan_Created_By"
#         )

#     def __str__(self):
#         return f'Shopping plan for {self.date}'

class ConversionRule(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, unique=True, db_column="ConvRule_Name")
    description = models.TextField(max_length=400, blank=True, null=True, db_column="ConvRule_Description")
    type = models.IntegerField(
        choices=wg_enumeration.ConversionRuleTypes.choices, blank=False, null=False, 
        default=wg_enumeration.ConversionRuleTypes.COMMON, db_column="ConvRule_Type"
        )
    products = models.ManyToManyField(Product, blank=False, db_column="ConvRule_Prod")
    from_unit = models.IntegerField(
        choices=wg_enumeration.VolumeUnits.choices, blank=False, null=False, db_column="ConvRule_From_Unit"
        )
    to_unit = models.IntegerField(
        choices=wg_enumeration.VolumeUnits.choices, blank=False, null=False, db_column="ConvRule_To_Unit"
        )
    ratio = models.FloatField(
        help_text="Ratio of 'To unit' to 'From unit' for a product.", validators=[MinValueValidator(0.0000000001)], 
        blank=False, null=False, db_column="ConvRule_Ratio"
        )
    created_on = models.DateTimeField(db_index=True, auto_now_add=True, db_column="ConvRule_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="ConvRule_Updated_On")
    created_by = models.ForeignKey(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="ConvRule_Created_By")

    def clean(self):
        # 'from_unit' and 'to_unit' cannot be the same
        if self.from_unit == self.to_unit:
            message = _('From_Unit and To_Unit can not be the same.')
            raise ValidationError({'from_unit': message, 'to_unit': message})

    def __str__(self):
        return f'Conversion rule to convert amount of {self.product.name} from {self.from_unit} to {self.to_unit}.'

class Config(models.Model):
    notify_by_email = models.BooleanField(blank=False, null=False, default=False, db_column="Conf_Notify_By_Email")

    notify_on_expiration = models.BooleanField(blank=False, null=False, default=True, db_column="Conf_Notify_Expire")
    notify_on_expiration_before = models.DurationField(
        blank=False, null=False, default=datetime.timedelta(days=7), db_column="Conf_Notify_Expired_Days"
        )
    default_expired_action = models.IntegerField(
        choices=wg_enumeration.EXPIRED_ACTIONS.choices, blank=False, null=False, 
        default=wg_enumeration.EXPIRED_ACTIONS.TRASH, 
        db_column="Conf_Default_Expired_Action"
        )
    prolong_expired_for = models.DurationField(
        blank=False, null=False, default=datetime.timedelta(days=7), db_column="Conf_Prolong_Expired_Days"
        )

    notify_on_min_stock = models.BooleanField(blank=False, null=False, default=True, db_column="Conf_Notify_Min_Stock")

    # nofity_on_shopping_plan_generated = models.BooleanField(
    #     blank=False, null=False, default=True, db_column="Conf_Notify_Shop_Plan_Gen"
    #     )

    # auto_generate_shopping_plan = models.BooleanField(
    #     blank=False, null=False, default=False, db_column="Conf_Gen_Shop_Plan"
    #     )
    allow_replacement_use = models.BooleanField(
        blank=False, null=False, default=False, db_column="Conf_Allow_Replacement"
        )
    # gen_shop_plan_on_min_stock = models.BooleanField(
    #     blank=False, null=False, default=False, db_column="Conf_Gen_ShopPlan_MinStock"
    #     )
    # gen_shop_plan_repeatedly = models.BooleanField(
    #     blank=False, null=False, default=False, db_column="Conf_Gen_ShopPlan_Repeatedly"
    #     )
    # gen_shop_plan_period = models.DurationField(
    #     blank=True, null=True, validators=[MinValueValidator(datetime.timedelta(days=3))], 
    #     default=datetime.timedelta(days=7), db_column="Conf_GenShopPlan_Periodicity"
    #     )
    base_shop_plan_on_historic_data = models.BooleanField(
        blank=False, null=False, default=True, db_column="Conf_Gen_ShopPlan_Historic"
        )
    historic_period = models.DurationField(
        blank=False, null=False, default=datetime.timedelta(days=30),
        validators=[MinValueValidator(datetime.timedelta(days=10))], 
        db_column="Conf_Hst_Period"
    )
    base_shop_plan_on_cook_plan = models.BooleanField(
        blank=False, null=False, default=True, db_column="Conf_Gen_ShopPlan_CookPlan"
        )

    created_on = models.DateTimeField(db_index=True, auto_now_add=True, db_column="Conf_Created_On")
    updated_on = models.DateTimeField(auto_now=True, db_column="Conf_Updated_On")
    created_by = models.OneToOneField(WiseGroceryUser, on_delete=models.CASCADE, blank=False, null=False, db_column="Conf_Created_By")
