from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .helpers import handle_stock_change
from .models import StockItem
from .tasks import stockitem_expired_handler
from .wg_enumeration import STOCK_STATUSES


@receiver(post_save, sender=StockItem)
def stockitem_volume_handler(sender, instance, created, update_fields, **kwargs):
    if created:
        #initiate task to set status expired on expiration
        try:
            stockitem_expired_handler.apply_async(({'pk': instance.pk},), eta=instance.use_till)
            handle_stock_change(instance)
        except Exception as e:
            print(e)

    if 'volume' in update_fields:
        try:
            handle_stock_change(instance)
        except Exception as e:
            print(e)

@receiver(pre_save, sender=StockItem)
def stockitem_status_handler(sender, instance, update_fields, **kwargs):
    if 'status' in update_fields and instance.status in [STOCK_STATUSES.COOKED, STOCK_STATUSES.WASTED]:
        instance.volume = 0
        