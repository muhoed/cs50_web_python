from django.db.models import Avg, F, Sum

from .helpers import get_conversion_ratio
from .models import *
from .wg_enumeration import *


class Shopping:
    def __init__(self, user: int) -> None:
        self.user = WiseGroceryUser.objects.get(pk=user)
        self.config = Config.objects.get(created_by=user)
        self.needed_products = {}
        self.shopping_list = []

    def generate_shopping_list(self) -> None:
        all_products = Product.objects.filter(created_by=self.user)
        # get active cooking plans if Base on cooking plans option enabled
        open_cook_plans = self.get_open_cooking_plans() if self.config.base_shop_plan_on_cook_plan else None
        # calculate needed products' quantities based on cook.plans if enabled
        if open_cook_plans != None:
            for plan in open_cook_plans:
                for recipe in plan.recipes.all():
                    for rec_prod in recipe.recipeproduct_set.all():
                        prod = all_products.get(pk=rec_prod.pk)
                        if rec_prod.unit != prod.unit:
                            conv_ratio = get_conversion_ratio(prod.pk, rec_prod.unit, prod.unit, rec_prod.created_by)
                        if rec_prod.pk not in self.needed_products.keys():
                            self.needed_products[rec_prod.pk] = rec_prod.volume / rec_prod.num_persons * plan.persons * conv_ratio
                        else:
                            self.needed_products[rec_prod.pk] += rec_prod.volume / rec_prod.num_persons * plan.persons * conv_ratio
        # get consumed product quantities if Base on historic data option is enabled
        consumption_history = self.get_consumption_history() if self.config.base_shop_plan_on_historic_data else None
        # calculate needed products' quantities based on hist.data if enabled
        consumed_totals_per_product = dict(
            (prod_avg.product, prod_avg.average_consumption) for prod_avg in consumption_history.values_list('product').annotate(
                average_consumption=Avg(F('quantity') * get_conversion_ratio(F('product'), F('unit'), F('product__unit'), self.user.pk))
                )
            )
        # compare and grab only highest needed quantity per product from cooking plan(s) and historical consumption
        if consumption_history != None:
            for key, value in self.needed_products.items():
                if key in consumed_totals_per_product.keys():
                    self.needed_products[key] = consumed_totals_per_product[key] if value < consumed_totals_per_product[key] else value
        # compare with min_stock values per product and amend if needed
        if self.config.gen_shop_plan_on_min_stock:
            for prod in all_products:
                if prod.minimal_stock_volume and prod.minimal_stock_volume > 0:
                    if prod.pk in self.needed_products.keys():
                        if prod.minimal_stock_volume > self.needed_products[prod.pk]:
                            self.needed_products[prod.pk] = prod.minimal_stock_volume
                    else:
                        self.needed_products[prod.pk] = prod.minimal_stock_volume
        # correct on existing stock volumes
        for key, value in self.needed_products:
            self.needed_products[key] -= StockItem.objects.filter(
                                                purchase_item__product = key,
                                                created_by = self.user
                                            ).exclude(
                                                status = STOCK_STATUSES.EXPIRED
                                            ).aggregate(Sum('volume'))[0].volume__sum

        # - generate a new shopping list
        self.shopping_list = list(ShoppingItem(product, quantity) for product, quantity in self.needed_products.items())

    def get_open_cooking_plans(self) -> object:
        # returns QuerySet object of CookingPlan model class filtered by current user and with Entered (open) status
        return CookingPlan.objects.filter(created_by=self.user, status=CookPlanStatuses.ENTERED)

    def get_consumption_history(self) -> object:
        # returns QuerySet object of Consumption model class filtered 
        return Consumption.objects.filter(
                type=ConsumptionTypes.COOKED,
                created_by=self.user,
                created_on__gte=datetime.now()-self.config.historic_period
            )


class ShoppingItem:
    def __init__(self, product: int, quantity: float) -> None:
        self.product = Product.objects.get(pk=product)
        self.unit = self.product.unit
        self.quantity = quantity
        self.current_stock = StockItem.objects.filter(
                                                purchase_item__product = product,
                                                created_by = self.product.created_by
                                            ).exclude(
                                                status = STOCK_STATUSES.EXPIRED
                                            ).aggregate(Sum('volume'))[0].sum_volume
        self.available_space = Equipment.objects.filter(
                                                min_tempreture__gte=self.product.min_tempreture,
                                                max_tempreture__lte=self.product.max_tempreture,
                                                free_space__gt=0,
                                                created_by=self.product.created_by
                                            ).aggregate(Sum('free_space'))