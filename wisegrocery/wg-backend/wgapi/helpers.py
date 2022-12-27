import datetime
from django.db.models import Case, F, OuterRef, Q, Subquery, Sum, When
from django.template.defaultfilters import slugify

from .models import Config, CookingPlan, Equipment, Product, ShoppingPlan, StockItem, ConversionRule
from .wg_enumeration import STOCK_STATUSES, CookPlanStatuses, ShopPlanStatuses, VolumeUnits


def get_icon_upload_path(stock_item, filename):
    instance_type = type(stock_item).__name__.lower()
    slug = slugify(stock_item.name)
    return "icons/%s/%s-%s" % (instance_type, slug, filename)

def handle_stock_change(stock_item, quantity):
    product = Product.objects.get(pk=stock_item.product, created_by=stock_item.created_by)
    equipment = Equipment.objects.get(pk=stock_item.equipment, created_by=stock_item.created_by)
    if stock_item.unit != product.unit:
        prod_conv_ratio = get_conversion_ratio(product.pk, stock_item.unit, product.unit, stock_item.created_by)
    if stock_item.unit != VolumeUnits.LITER:
        equip_conv_ratio = get_conversion_ratio(stock_item.product, stock_item.unit, VolumeUnits.LITER, stock_item.created_by)
    product.current_stock += quantity * prod_conv_ratio
    product.save()
    equipment.free_space -= quantity * equip_conv_ratio
    equipment.save()

def send_notification(object, type, email):
    # TODO: logic to send push notification or message through websocket

    if email:
        # TODO: logic to senf notification by 
        pass
    pass

def store_purchased_item(item):
    try:
        product = Product.objects.get(pk=item.product, created_by=item.created_by)
        equipment = Equipment.objects.filter(
                min_tempreture__gte=product.min_tempreture,
                max_tempreture__lte=product.max_tempreture,
                free_space__gt=0,
                created_by=item.created_by
            ).prefetch_related('stockitem_set').order_by('-free_space')
        if item.unit != VolumeUnits.LITER:
            conv_ratio = get_conversion_ratio(product, item.unit, VolumeUnits.LITER, item.created_by)
        quantity = item.volume
        # first try to put purchased item to equipment where similar items are already stored
        for e in equipment:
            capacity = e.free_space / conv_ratio
            if e.stockitem_set.filter(product=product).exists():
                new_stock_item = StockItem.objects.create(
                    product = product,
                    equipment = e,
                    unit = item.unit,
                    volume = quantity if capacity >= quantity else capacity
                )
                quantity -= new_stock_item.volume
            if quantity == 0:
                break
        # if some quantity still not stored, try to put it into suitable equipment with free space
        if quantity > 0:
            # we need to retrieve equipment again to get current free space
            # we also do not need stored stock items info anymore
            equipment = Equipment.objects.filter(
                    min_tempreture__gte=product.min_tempreture,
                    max_tempreture__lte=product.max_tempreture,
                    free_space__gt=0,
                    created_by=item.created_by
                ).order_by('free_space')
            for e in equipment:
                capacity = e.free_space / conv_ratio
                new_stock_item = StockItem.objects.create(
                    product = product,
                    equipment = e,
                    unit = item.unit,
                    volume = quantity if capacity >= quantity else capacity
                )
                quantity -= new_stock_item.volume
                if quantity == 0:
                    break
        # if some quantity not stored even now, store it with NOTPLACED status for further manual alocation
        if quantity > 0:
            new_stock_item = StockItem.objects.create(
                    product = product,
                    equipment = e,
                    unit = item.unit,
                    volume = quantity,
                    status = STOCK_STATUSES.NOTPLACED
                )
    except Exception as ex:
        print(ex)

def handle_cooking_plan_fulfillment(obj):
    # handle stock of products used in cooked plan fulfillment
    for recipe in obj.recipes.all():
        for prod_recipe in recipe.recipeproduct_set.all():
            quantity = prod_recipe.volume
            stockitems = StockItem.objects.filter(
                    product=prod_recipe.product
                ).order_by('created_on')
            for item in stockitems:
                if prod_recipe.unit != item.unit:
                    ratio = get_conversion_ratio(prod_recipe.product, prod_recipe.unit, item.unit, item.created_by)
                if item.volume <= quantity * ratio:
                    item.status = STOCK_STATUSES.COOKED
                    quantity -= item.volume
                else:
                    handle_stock_change(item, quantity * ratio)
                    quantity = 0
                    item.volume -= quantity * ratio
                item.save()
                if quantity == 0:
                    break

def generate_shopping_plan(config):
    # get shopping plans in Entered or Partially fulfilled status to avoid duplicates
    open_shop_plans = ShoppingPlan.objects.filter(created_by=config.created_by, status=ShopPlanStatuses.ENTERED)
    partial_shop_plans = ShoppingPlan.objects.filter(created_by=config.created_by, status=ShopPlanStatuses.PARTIALLY_FULFILLED)
    # get active cooking plans if Base on cooking plans option enabled
    open_cook_plans = None
    if config.base_shop_plan_on_cook_plan:
        open_cook_plans = CookingPlan.objects.filter(created_by=config.created_by, status=CookPlanStatuses.ENTERED)
    # get consumed product quantities if Base on historic data option is enabled
    consumed_stock_items = None
    if config.base_shop_plan_on_historic_data:
        consumed_stock_items = StockItem.objects.filter(
                created_by=config.created_by,
                created_on__gte=datetime.now()-config.historic_period
            ).exclude(volume=F('initial_volume'))
    # to be done:
    # - calculate needed products' quantities based on cook.plans if enabled
    # - calculate needed products' quantities based on hist.data if enabled
    # - compare and grab only highest needed quantity pre product
    # - close all open/partially fulfilled shopping plans
    # - generate a new shopping plan (-s)
    # - send notification

def get_conversion_ratio(product, unit1, unit2, owner):
    try:
        conv_rule = ConversionRule.objects.get(
                                product=product,
                                unit_from=unit1,
                                unit_to=unit2,
                                created_by=owner
                            ).values('ratio')
        if not conv_rule:
            conv_rule = ConversionRule.objects.get(
                                product=product,
                                unit_from=unit2,
                                unit_to=unit1,
                                created_by=owner
                            ).value('ratio')
            conv_ratio = 1 / conv_ratio
    except Exception as e:
        print(e)
    if not conv_rule:
        return 1
    return conv_rule['ratio']
