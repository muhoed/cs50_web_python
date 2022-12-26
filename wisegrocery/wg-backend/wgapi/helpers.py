from django.db.models import Case, F, OuterRef, Q, Subquery, Sum, When
from django.template.defaultfilters import slugify

from .models import Equipment, Product, StockItem, ConversionRule
from .wg_enumeration import STOCK_STATUSES, VolumeUnits


def get_icon_upload_path(stock_item, filename):
    instance_type = type(stock_item).__name__.lower()
    slug = slugify(stock_item.name)
    return "icons/%s/%s-%s" % (instance_type, slug, filename)

# def get_conversion_rules_for_queryset(queryset):
#         stock_items = StockItem.objects.filter(
#                 pk=OuterRef('stockitem_set__pk')
#             ).exclude(
#                 status__in=[
#                     STOCK_STATUSES.COOKED, 
#                     STOCK_STATUSES.WASTED,
#                     ]
#             )
#         prod_conv_rule = ConversionRule.objects.filter(
#             product=OuterRef('product__pk'),
#             unit_to=VolumeUnits.LITER,
#             unit_from=OuterRef('unit')
#             ).values('ratio')
#         stock_items.annotate(conv_ratio=Subquery(prod_conv_rule))
#         return queryset.annotate(
#             stock_volume=Sum(
#                 Subquery(
#                     Case(
#                         When(Q(stock_items_unit=VolumeUnits.LITER), then=F('stock_items_volume')),
#                         When(Q(stock_items_conv_rule__isnull=True), then=1),
#                         default=F('stock_items_volume') * F('stock_items_conv_ratio')),
#                         )
#                 )
#             )

def handle_stock_change(stock_item):
    product = Product.objects.get(pk=stock_item.product)
    equipment = Equipment.objects.get(pk=stock_item.equipment)
    if stock_item.unit != product.unit:
        prod_conv_rule = ConversionRule.objects.get(
            product=product.pk,
            from_unit=stock_item.unit,
            to_unit=product.unit
            )
    if stock_item.unit != VolumeUnits.LITER:
        equip_conv_rule = ConversionRule.objects.get(
            product=stock_item.product,
            from_unit=stock_item.unit,
            to_unit=VolumeUnits.LITER
        )
    product.current_stock += stock_item.volume * prod_conv_rule.ratio if prod_conv_rule \
        else stock_item.volume
    product.save()
    equipment.free_space -= stock_item.volume * equip_conv_rule.ratio if equip_conv_rule \
        else stock_item.volume
    equipment.save()
