from django_filters import rest_framework as filters

from .models import CookingPlan, Equipment, Product, PurchaseItem, Recipe, ShoppingPlan, StockItem
from .wg_enumeration import Meals, STOCK_STATUSES


class EquipmentFilterSet(filters.FilterSet):
    min_tempreture = filters.NumberFilter(field_name='min_tempreture', lookup_expr='gte')
    max_tempreture = filters.NumberFilter(field_name='max_tempreture', lookup_expr='lte')
    free_space = filters.NumberFilter(field_name='free_space', lookup_expr='gte')

    class Meta:
        model = Equipment
        fields = ['created_by']

class ProductFilterSet(filters.FilterSet):
    current_stock = filters.NumberFilter(field_name='current_stock', lookup_expr='gte')
    low_stock = filters.NumberFilter(field_name='current_stock', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category', 'recipe', 'created_by']

class StockItemFilterSet(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=STOCK_STATUSES, conjoined=False)

    class Meta:
        model = StockItem
        fields = ['status', 'created_by']

class RecipeFilterSet(filters.FilterSet):
    num_persons = filters.RangeFilter()
    cooking_time = filters.RangeFilter()

    class Meta:
        model = Recipe
        fields = ['product', 'num_persons', 'cooking_time', 'created_by']

class CookingPlanFilterSet(filters.FilterSet):
    meal = filters.MultipleChoiceFilter(choices=Meals, conjoined=False)
    date = filters.DateFromToRangeFilter()
    persons = filters.RangeFilter()

    class Meta:
        model = CookingPlan
        fields = ['meal', 'date', 'persons', 'recipe', 'status', 'created_by']

class PurchaseItemFilterSet(filters.FilterSet):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'shop_plan', 'status', 'created_by']

class ShoppingPlanFilterSet(filters.FilterSet):
    date = filters.DateFromToRangeFilter()

    class Meta:
        model = ShoppingPlan
        fields = ['date', 'purchaseitem_set', 'created_by']
