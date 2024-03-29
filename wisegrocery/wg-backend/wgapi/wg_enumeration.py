from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


class BaseEquipmentTypes(models.TextChoices):
    FREEZER = 'FRE', _('Freezer')
    FRIDGE = 'FRD', _('Fridge')
    BUFFET = 'BFT', _('Buffet')
    CUPBOARD ='CBD', _('Cupboard')

BASE_EQUIPMENT_TEMPS = {
    BaseEquipmentTypes.FREEZER.value: (-25.0, -15.0),
    BaseEquipmentTypes.FRIDGE.value: (7.0, 12.0),
    BaseEquipmentTypes.BUFFET.value: (15, 25),
    BaseEquipmentTypes.CUPBOARD.value: (15, 30),
}

BASE_EQUIPMENT_ICONS = {
    BaseEquipmentTypes.FREEZER.value: ('freezer.png', _('Freezer')),
    BaseEquipmentTypes.FRIDGE.value: ('fridge.png', _('Fridge')),
    BaseEquipmentTypes.BUFFET.value: ('buffet.png', _('Buffet')),
    BaseEquipmentTypes.CUPBOARD.value: ('cupboard.png', _('Cupboard')),
}

class ProductCategories(models.IntegerChoices):
    FRUITS = 1, _('Fruits')
    VEGETABLES = 2, _('Vegetables')
    DAIRY = 3, _('Dairy')
    BAKED_GOODS = 4, _('Baked goods')
    MEAT = 5, _('Meat')
    FISH = 6, _('Fish')
    MEAT_ALTERNATIVES = 7, _('Meat alternatives')
    CANS_AND_JARS = 8, _('Cans and Jars')
    PASTA_RICE_CEREALS = 9, _('Pasta, rice, cereals')
    SAUCES_AND_CONDIMENTS = 10, _('Sauces and Condiments')
    HERBS_AND_SPICES = 11, _('Herbs and Spices')
    FROZEN_FOODS = 12, _('Frozen foods')
    SNACKS = 13, _('Snacks')
    DRINKS = 14, _('Drinks')
    HOUSEHOLD_AND_CLEANING = 15, _('Household and Cleaning')
    PERSONAL_CARE = 16, _('Personal care')
    PET_CARE = 17, _('Pet care')
    BABY_PRODUCTS = 18, _('Baby products')
    MILK_PRODUCTS = 19, _('Milk products')
    OTHER = 20, _('Other')

class VolumeUnits(models.IntegerChoices):
    LITER = 1, _('Liter')
    MILLILITER = 2, _('Milliliter')
    GALLON = 3, _('Gallon')
    GRAM = 4, _('gram')
    KILOGRAM = 5, _('kilogram')
    POUND = 6, _('pound')
    OUNCE = 7, _('ounce')
    PIECE = 8, _('Piece')
    PACK = 9, _('Pack')
    CAN = 10, _('Can')
    BOTTLE = 11, _('Bottle')
    CUP = 12, _('Cup')
    SPOON = 13, _('Spoon')
    TEASPOON = 14, _('Teaspoon')

class Meals(models.IntegerChoices):
    BREAKFAST = 1, _('Breakfast')
    LUNCH = 2, _('Lunch')
    DINNER = 3, _('Dinner')

class PurchaseStatuses(models.IntegerChoices):
    BOUGHT = 0, _('bougth')
    PARTIALLY_STORED = 1, _('partially stored')
    STORED = 2, _('stored')
    MOVED = 3, _('moved')

class STOCK_STATUSES(models.IntegerChoices):
    ACTIVE = 0, _('Active')
    EXPIRED = 1, _('Expired')
    NOTPLACED = 2, _('Not placed')
    TRASHED = 3, _('Trashed')

class EXPIRED_ACTIONS(models.IntegerChoices):
    TRASH = 0, _('Trash')
    ALLOW = 1, _('Allow')
    PROLONG = 2, _('Prolong')

class ConsumptionTypes(models.IntegerChoices):
    COOKED = 0, _('Cooked')
    TRASHED = 1, _('Trashed')
    OTHER = 2, _('Other')

class PurchaseTypes(models.IntegerChoices):
    PURCHASE = 0, _('Purchase')
    BALANCE = 1, _('Balance entry / correction')

class NotificationTypes(models.IntegerChoices):
    EXPIRATION = 0, _('Expiration')
    OUTAGE = 1, _('Outage')
    TRASH = 2, _('Stock item trashed')
    SHOPPINGPLAN = 3, _('Cooking plan generated')
    BEFOREXPIRATION = 4, _('Stock item will expire soon')

class CookPlanStatuses(models.IntegerChoices):
    ENTERED = 0, _('Entered')
    COOKED = 1, _('Cooked')

# class ShopPlanStatuses(models.IntegerChoices):
#     ENTERED = 0, _('Entered')
#     FULFILLED = 1, _('Fulfilled')
#     PARTIALLY_FULFILLED = 3, _('Partially fulfilled')
#     CLOSED = 4, _('Closed')

class ConversionRuleTypes(models.IntegerChoices):
    COMMON = 0, _('Common conversion rule')
    SPECIFIC = 1, _('Product specific conversion rule')
