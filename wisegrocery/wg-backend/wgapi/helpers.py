import datetime
from django.db.models import F
from django.template.defaultfilters import slugify

from .models import *
from .wg_enumeration import *


# def handle_stock_change(stock_item, quantity):
#     product = Product.objects.get(pk=stock_item.product, created_by=stock_item.created_by)
#     equipment = Equipment.objects.get(pk=stock_item.equipment, created_by=stock_item.created_by)
#     if stock_item.unit != product.unit:
#         prod_conv_ratio = get_conversion_ratio(product.pk, stock_item.unit, product.unit, stock_item.created_by)
#     if stock_item.unit != VolumeUnits.LITER:
#         equip_conv_ratio = get_conversion_ratio(stock_item.product, stock_item.unit, VolumeUnits.LITER, stock_item.created_by)
#     product.current_stock += quantity * prod_conv_ratio
#     product.save()
#     equipment.free_space -= quantity * equip_conv_ratio
#     equipment.save()

def send_notification(item: object, type: NotificationTypes, send_email: bool) -> None:
    """Creates new stock item(s) on Purchase or after existing PurchaseItem or Consumption record 
    modification led to increase of inventory.

    Parameters
    ----------
    item : object
        instance of class triggered notification
    type : NotificationTypes
        enumeration value of notification type
    send_email : bool
        flag triggering email notification

    Returns
    -------
    None
    """
    # TODO: logic to send push notification or message through websocket

    if send_email:
        # TODO: logic to senf notification by 
        pass
    pass

def post_inventory(item: object, quantity: float) -> None:
    """Creates new stock item(s) on Purchase or after existing PurchaseItem or Consumption record 
    modification led to increase of inventory.

    Parameters
    ----------
    item : object
        instance of PurchaseItem or Consumption class
    quantity : float
        quantity of Item product to be stored

    Returns
    -------
    None
    """
    try:
        # place into suitable equipemnt
        product = Product.objects.get(pk=item.product, created_by=item.created_by)
        equipment = Equipment.objects.filter(
                min_tempreture__gte=product.min_tempreture,
                max_tempreture__lte=product.max_tempreture,
                free_space__gt=0,
                created_by=item.created_by
            ).prefetch_related('stockitem_set').order_by('free_space')
        if item.unit != VolumeUnits.LITER:
            conv_ratio = get_conversion_ratio(product.pk, item.unit, VolumeUnits.LITER, item.created_by)
        
        # handle purchase
        if isinstance(item, Purchase):
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
                    e.free_space = e.free_space - quantity * conv_ratio if capacity >= quantity else 0
                    e.save()
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
                    e.free_space = e.free_space - quantity * conv_ratio if capacity >= quantity else 0
                    e.save()
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
                item.status = PurchaseStatuses.PARTIALLY_STORED
            else:
                item.status = PurchaseStatuses.STORED
            item.save()
        else:
            # implementation of consumption post to inventory
            #  TODO
            raise Exception('Not implemented')
    except Exception as ex:
        print(ex)

def update_inventory_record(item: object) -> None:
    """Updates or creates new stock item(s) after existing PurchaseItem or Consumption record was modified.

    Parameters
    ----------
    item : object
        instance of PurchaseItem or Consumption class

    Returns
    -------
    None
    """
    type = 1
    if isinstance(item, Consumption):
        type = 2

    try:
        #update stock in equipmentif item.unit != VolumeUnits.LITER:
        eq_conv_ratio = get_conversion_ratio(item.product, item.unit, VolumeUnits.LITER, item.created_by) if item.unit != VolumeUnits.LITER else 1
        conv_ratio = get_conversion_ratio(item.product, item._original_unit, item.unit, item.created_by) if item._original_unit != item.unit else 1
        
        quantity_change = (item.quantity - item._original_quantity * conv_ratio) if type == 1 else (item._original_quantity * conv_ratio - item.quantity)
        
        if type == 1:
            product_stock = StockItem.objects.filter(
                                                    purchase_item=item,
                                                    created_by=item.created_by
                                                ).prefetch_related(
                                                    'equipment'
                                                ).order_by('-created_by')
        else:
            product_stock = StockItem.objects.filter(
                                                    purchase_item__product=item.product,
                                                    created_by=item.created_by
                                                ).prefetch_related(
                                                    'equipment'
                                                ).order_by('-created_by')

        # do nothing if quantity wasn't changed
        if quantity_change == 0:
            return
        # decrease stored quantity if purchased quantity was reduced
        if quantity_change < 0:
            for stock_item in product_stock:
                conv_ratio = get_conversion_ratio(item.product, item.unit, stock_item.unit, item.created_by) if item.unit != stock_item.unit else 1
                if quantity_change < 0 and stock_item.volume >= abs(quantity_change) * conv_ratio:
                    stock_item.volume += quantity_change * conv_ratio
                    stock_item.equipment.free_space -= quantity_change * eq_conv_ratio
                    stock_item.equipment.save()
                    stock_item.save()
                    break
                elif quantity_change < 0 and stock_item.volume < abs(quantity_change) * conv_ratio:
                    stock_item.equipment.free_space += stock_item.volume / conv_ratio * eq_conv_ratio
                    stock_item.equipment.save()
                    quantity_change = quantity_change + stock_item.volume / conv_ratio
                    stock_item.delete()
            if quantity_change != 0:
                raise Exception('Stored quantity of the product can not be negative.')
        else:
            if type == 1:
                post_inventory(item, quantity_change)
            else:
                # create Purchase of balance / correction type with respective PurchaseItem to store additional quantity
                # post to inventory will be triggered in post_save signal of PurchaseItem instance
                new_purchase = Purchase.objects.create(
                    date = item.date,
                    type = PurchaseTypes.BALANCE,
                    note = 'System purchase created to correct inventory balance due to reducing of quantity on an existing Consumption record.'
                )
                PurchaseItem.objects.create(
                    purchase = new_purchase,
                    product = item.product,
                    unit = item.unit,
                    quantity = quantity_change,
                    status = PurchaseStatuses.MOVED
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
    all_products = Product.objects.filter(created_by=config.created_by)
    # get shopping plans in Entered or Partially fulfilled status to avoid duplicates
    open_shop_plans = ShoppingPlan.objects.filter(
        created_by=config.created_by, 
        status__in=[ShopPlanStatuses.ENTERED, ShopPlanStatuses.PARTIALLY_FULFILLED]
        ).prefetch_related('purchaseitem_set')
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
    # dictionary to keep products for purchase
    needed_products = {}
    # calculate needed products' quantities based on cook.plans if enabled
    if open_cook_plans:
        for plan in open_cook_plans:
            for recipe in plan.recipes.all():
                for rec_prod in recipe.recipeproduct_set.all():
                    prod = all_products.get(pk=rec_prod.pk)
                    if rec_prod.unit != prod.unit:
                        conv_ratio = get_conversion_ratio(prod.pk, rec_prod.unit, prod.unit, rec_prod.created_by)
                    if rec_prod.pk not in needed_products.keys():
                        needed_products[rec_prod.pk] = rec_prod.volume * conv_ratio
                    else:
                        needed_products[rec_prod.pk] += rec_prod.volume * conv_ratio
    # calculate needed products' quantities based on hist.data if enabled
    consumed_totals_per_product = {}
    if consumed_stock_items:
        for item in consumed_stock_items:
            prod = all_products.get(pk=item.product)
            if item.unit != prod.unit:
                conv_ratio = get_conversion_ratio(prod.pk, item.unit, prod.unit, item.created_by)
            if prod.pk not in consumed_totals_per_product.keys():
                consumed_totals_per_product[prod.pk] = (item.initial_volume - item.volume) * conv_ratio
            else:
                consumed_totals_per_product[prod.pk] += (item.initial_volume - item.volume) * conv_ratio
    # forecast consumption based on historic data averages
    for key, value in consumed_totals_per_product.items():
        consumed_totals_per_product[key] = value / config.historic_period.days * config.gen_shop_plan_period
    # compare and grab only highest needed quantity per product
    for key, value in needed_products.items():
        if key in consumed_totals_per_product.keys():
            needed_products[key] = consumed_totals_per_product[key] if value < consumed_totals_per_product[key] else value
    # compare with min_stock values per product and amend if needed
    if config.gen_shop_plan_on_min_stock:
        for prod in all_products:
            if prod.minimal_stock_volume and prod.minimal_stock_volume > 0:
                if prod.pk in needed_products.keys():
                    needed_products[prod.pk] = prod.minimal_stock_volume if prod.minimal_stock_volume > needed_products[key] else value
                else:
                    needed_products[prod.pk] = prod.minimal_stock_volume
    # close all open/partially fulfilled shopping plans
    for plan in open_shop_plans:
        for item in plan.purchaseitem_set:
            item.status = PurchaseStatuses.MOVED
            item.save()
        plan.status = ShopPlanStatuses.CLOSED
        plan.save()
    # - generate a new shopping plan (-s)
    new_shop_plan = ShoppingPlan.objects.create(
        date = datetime.now() + datetime.timedalte(days=1),
        note = f'Shopping plan generated on {datetime.now()}. \
            Generation settings: \
             - Base on minimal stock level = {"Yes" if config.gen_shop_plan_on_min_stock else "No"} \
             - Base on historic consumption = {"Yes" if config.base_shop_plan_on_historic_data else "No"}',
            #  - Autogeneration  = {"Yes" if config.auto_generate_shopping_plan else "No"} \
            #  - Generate shopping plan repeatedly = {"Yes" if config.gen_shop_plan_repeatedly else "No"} \
            #  - Base on minimal stock level = {"Yes" if config.gen_shop_plan_on_min_stock else "No"} \
            #  - Base on historic consumption = {"Yes" if config.base_shop_plan_on_historic_data else "No"}', \
            #  - Base on cooking plans = {"Yes" if config.base_shop_plan_on_cook_plan else "No"}',
        created_by = config.created_by
    )
    for key, value in needed_products.items():
        prod = all_products.get(pk=key)
        purch_item = PurchaseItem.objects.create(
            product = prod,
            shop_plan = new_shop_plan.pk,
            unit = prod.unit,
            volume = value,
            status = PurchaseStatuses.TOBUY,
            created_by = config.created_by
        )
        purch_item.save()
    # send notification
    send_notification(new_shop_plan, NotificationTypes.SHOPPINGPLAN, config.notify_by_email)

def get_conversion_ratio(prod_pk, unit1, unit2, owner):
    try:
        conv_rule = ConversionRule.objects.filter(
                                products__pk=prod_pk,
                                unit_from=unit1,
                                unit_to=unit2,
                                created_by=owner
                            ).values('ratio').first()
        if not conv_rule:
            conv_rule = ConversionRule.objects.get(
                                products__pk=prod_pk,
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
