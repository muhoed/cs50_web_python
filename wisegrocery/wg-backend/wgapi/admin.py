from django.contrib import admin

from .models import *

# Register your models here.
@admin.register(WiseGroceryUser, Config)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(EquipmentType, Equipment, Product, StockItem, ConversionRule)
class StockManagementAdmin(admin.ModelAdmin):
    pass

@admin.register(Recipe, RecipeProduct, CookingPlan)
class CookingPlanAdmin(admin.ModelAdmin):
    pass

@admin.register(PurchaseItem, ShoppingPlan)
class ShoppingPlanAdmin(admin.ModelAdmin):
    pass
