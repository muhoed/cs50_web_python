from django_filters import rest_framework as filters

from .models import CookingPlan, Equipment, Product, PurchaseItem, Recipe, Purchase, StockItem
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
        fields = ['items', 'num_persons', 'cooking_time', 'created_by']

class CookingPlanFilterSet(filters.FilterSet):
    meal = filters.MultipleChoiceFilter(choices=Meals, conjoined=False)
    date = filters.DateFromToRangeFilter()
    persons = filters.RangeFilter()

    class Meta:
        model = CookingPlan
        fields = ['meal', 'date', 'persons', 'recipes', 'status', 'created_by']

class PurchaseFilterSet(filters.FilterSet):
    date = filters.DateFromToRangeFilter()

    class Meta:
        model = Purchase
        fields = ['date', 'type', 'created_by']

class PurchaseItemFilterSet(filters.FilterSet):
    class Meta:
        model = PurchaseItem
        fields = ['purchase', 'product', 'status', 'created_by']

class ConsumptionFilterSet(filters.FilterSet):
    date = filters.DateFromToRangeFilter()
    class Meta:
        model = PurchaseItem
        fields = ['date', 'product', 'cooking_plan', 'recipe_product', 'type', 'created_by']

# class ShoppingPlanFilterSet(filters.FilterSet):
#     date = filters.DateFromToRangeFilter()

#     class Meta:
#         model = ShoppingPlan
#         fields = ['date', 'created_by']
