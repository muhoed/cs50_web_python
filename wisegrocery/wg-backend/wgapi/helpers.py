import datetime
from functools import partial
from django.db import transaction
from django.db.models import F, Sum
from django.template.defaultfilters import slugify

from .models import *
from .wg_enumeration import *


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

def check_minimal_stock(product: object) -> bool:
    """Checks if minimal stock quantity requirement for a product is not met.
    Send a notification if configured in Config.

    Parameters
    ----------
    product : object
        instance of Product to check minimal stock requirement for

    Returns
    -------
    bool
        True - minimal stock requirement met
        False - minimal stock requirement not met
    """
    try:
        current_stock = StockItem.objects.filter(
            purchase_item__product=product.pk,
            created_by=product.created_by
        ).aggregate(Sum('volume'))
        if current_stock['volume__sum'] <= product.minimal_stock_volume:
            return False
        return True
    except Exception as e:
        print('Check minimal stock exception.')
        raise e

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
    initial_quantity = quantity
    config = Config.objects.get(created_by=item.created_by)
    product = item.product # Product.objects.get(pk=item.product, created_by=item.created_by)
    to_prod_conv_ratio = get_conversion_ratio(product.pk, item.unit, product.unit, item.created_by)
    # place into suitable equipemnt
    if item.unit != VolumeUnits.LITER:
        conv_ratio = get_conversion_ratio(product.pk, item.unit, VolumeUnits.LITER, item.created_by)
    
    # handle purchase
    if isinstance(item, PurchaseItem):
        # first try to put purchased item to equipment where similar items are already stored
        equipment = Equipment.objects.filter(
                min_tempreture__gte=product.min_tempreture,
                max_tempreture__lte=product.max_tempreture,
                free_space__gt=0,
                created_by=item.created_by
            ).prefetch_related('stockitem_set').order_by('free_space')
        
        quantity = store_purchase_item(item, quantity, product.unit, equipment, conv_ratio, to_prod_conv_ratio, existing=True)
        
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
            
            quantity = store_purchase_item(item, quantity, product.unit, equipment, conv_ratio, to_prod_conv_ratio)

        # if some quantity not stored even now, store it with NOTPLACED status for further manual alocation
        if quantity > 0:
            StockItem.objects.create(
                    purchase_item = item,
                    unit = product.unit,
                    volume = quantity * to_prod_conv_ratio,
                    use_till = item.use_till,
                    status = STOCK_STATUSES.NOTPLACED,
                    created_by=item.created_by
                )
            if quantity < initial_quantity:
                item.status = PurchaseStatuses.PARTIALLY_STORED
        else:
            item.status = PurchaseStatuses.STORED
        item.save(update_fields=['status'])
    else:
        # post consumption record to inventory
        stock_items = StockItem.objects.filter(
            purchase_item__product = product.pk,
            created_by = item.created_by,
            status__in = [STOCK_STATUSES.ACTIVE, STOCK_STATUSES.NOTPLACED]
        ).order_by('created_on')
        for stock_item in stock_items:
            if quantity > 0:
                conv_ratio1 = get_conversion_ratio(product.pk, stock_item.unit, item.unit, item.created_by)
                equipment = Equipment.objects.filter(pk=stock_item.equipment).first()
                if stock_item.volume / conv_ratio1 <= quantity:
                    quantity = quantity - stock_item.volume / conv_ratio1
                    if equipment:
                        equipment.free_space += stock_item.volume / conv_ratio1 * conv_ratio
                    if item.type == ConsumptionTypes.TRASHED:
                        transaction.on_commit(partial(
                            send_notification, 
                            item=stock_item, 
                            type=NotificationTypes.TRASH, 
                            send_email=config.notify_by_email
                            ))
                    stock_item.delete()
                else:
                    stock_item.volume = stock_item.volume - quantity * conv_ratio1
                    stock_item.save()
                    if equipment:
                        equipment.free_space += quantity * conv_ratio
                    quantity = 0
                if equipment:
                    equipment.save()
        if quantity > 0:
            raise Exception(f'Stored quantity of the product can not be negative. Quantity is -{quantity}')
    
    if not check_minimal_stock(product) and config.notify_on_min_stock:
        # send notification
        transaction.on_commit(partial(
            send_notification,
            item=product, 
            type=NotificationTypes.OUTAGE, 
            send_email=config.notify_by_email
            ))

def store_purchase_item(item: object, quantity: Decimal, unit: int, equipment: [object], conv_ratio: Decimal, to_prod_conv_ratio: Decimal, existing : bool = False) -> Decimal:
    """Creates new stock item(s) on PurchaseItem creation or after existing PurchaseItemrecord 
    modification leading to increase of inventory.

    Parameters
    ----------
    item : object
        instance of PurchaseItem class
    quantity : float
        quantity of product to be stored
    unit : int
        VolumeUnits enum value
    equipment : [object]
        list of Equipment objects to store in
    conv_ratio : Decimal
        conversion ratio to convert quantity units into equipment units (liter)
    to_prod_conv_ratio : float
        conversion ratio to convert quantity units into product / stock units
    existing : bool
        defines whether to check that equipment is already used for this product or not;
        default value is False

    Returns
    -------
    Decimal
        remaining (not stored) quantity
    """
    for e in equipment:
        capacity = e.free_space / conv_ratio
        if existing:
            if e.stockitem_set.filter(purchase_item__product=item.product).exists():
                new_stock_item = StockItem.objects.create(
                    purchase_item = item,
                    equipment = e,
                    unit = unit,
                    volume = (quantity if capacity >= quantity else capacity) * to_prod_conv_ratio,
                    use_till = item.use_till,
                    created_by=item.created_by
                )
                e.free_space = (e.free_space - quantity * conv_ratio) if capacity >= quantity else 0
                e.save()
                quantity -= new_stock_item.volume / to_prod_conv_ratio
            if quantity == 0:
                break
        else:
            new_stock_item = StockItem.objects.create(
                    purchase_item = item,
                    equipment = e,
                    unit = unit,
                    volume = (quantity if capacity >= quantity else capacity) * to_prod_conv_ratio,
                    use_till = item.use_till,
                    created_by=item.created_by
                )
            e.free_space = (e.free_space - quantity * conv_ratio) if capacity >= quantity else 0
            e.save()
            quantity -= new_stock_item.volume / to_prod_conv_ratio
            if quantity == 0:
                break

    return Decimal(quantity)

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
    
    #update stock in equipmentif item.unit != VolumeUnits.LITER:
    eq_conv_ratio = get_conversion_ratio(item.product.id, item.unit, VolumeUnits.LITER, item.created_by) if item.unit != VolumeUnits.LITER else 1
    conv_ratio = get_conversion_ratio(item.product.id, item._original_unit, item.unit, item.created_by) if item._original_unit != item.unit else 1
    
    quantity_change = Decimal(item.quantity - item._original_quantity * conv_ratio) if type == 1 else Decimal(item._original_quantity * conv_ratio - item.quantity)
    
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
            conv_ratio = get_conversion_ratio(item.product.id, item.unit, stock_item.unit, item.created_by) if item.unit != stock_item.unit else 1
            if quantity_change < 0 and stock_item.volume >= abs(quantity_change * conv_ratio):
                stock_item.volume += quantity_change * conv_ratio
                if stock_item.equipment:
                    stock_item.equipment.free_space -= quantity_change * eq_conv_ratio
                    stock_item.equipment.save()
                stock_item.save()
                quantity_change = 0
                break
            elif quantity_change < 0 and stock_item.volume < abs(quantity_change * conv_ratio):
                if stock_item.equipment:
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
                use_till = product_stock[0].use_till,
                status = PurchaseStatuses.MOVED
            )

def handle_cooking_plan_fulfillment(obj: object) -> None:
    """Creates Consumption records after Cooking Plan was marked as fulfilled.

    Parameters
    ----------
    obj : object
        instance of CookingPlan class

    Returns
    -------
    None
    """
    for recipe in obj.recipes.all():
        for recipe_prod in recipe.recipeproduct_set.all():
            Consumption.objects.create(
                product = recipe_prod.product,
                cooking_plan = obj,
                recipe_product = recipe_prod,
                date = datetime.datetime.now(),
                type = ConsumptionTypes.COOKED,
                unit = recipe_prod.unit,
                quantity = recipe_prod.volume / recipe.num_persons * obj.persons,
                created_by = obj.created_by
            )

def get_conversion_ratio(prod_pk: int, unit1: VolumeUnits, unit2: VolumeUnits, owner: int) -> Decimal:
    """Returns convertion ratio to convert quantity/volume from unit1 to unit2.

    Parameters
    ----------
    prod_pk : int
        Key of Product instance
    unit1 : VolumeUnits
        Enumeration value of unit1 type
    unit2 : VolumeUnits enumeration value
        Enumeration value of unit2 type
    owner : int
        Key of User instance

    Returns
    -------
    conv_rule.ratio : Decimal
        convertion ratio or 1 if isn't defined
    """
    conv_ratio = 1
    conv_rule = ConversionRule.objects.filter(
                            products__pk=prod_pk,
                            from_unit=unit1,
                            to_unit=unit2,
                            created_by=owner
                        ).values('ratio')
    if not conv_rule:
        conv_rule = ConversionRule.objects.filter(
                            products__pk=prod_pk,
                            from_unit=unit2,
                            to_unit=unit1,
                            created_by=owner
                        ).values('ratio')
        if conv_rule:
            conv_ratio = 1 / conv_rule[0]['ratio']
    else:
        conv_ratio = conv_rule[0]['ratio']
    return Decimal(conv_ratio)
