import datetime
import json

from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .helpers import generate_shopping_plan, handle_cooking_plan_fulfillment, handle_stock_change, send_notification, store_purchased_item
from .models import Config, CookingPlan, Product, PurchaseItem, ShoppingPlan, StockItem
from .tasks import repeat_shopping_plan_generator, stockitem_expired_handler
from .wg_enumeration import STOCK_STATUSES, CookPlanStatuses, NotificationTypes, PurchaseStatuses, ShopPlanStatuses


@receiver(post_save, sender=StockItem)
def stockitem_handler(sender, instance, created, update_fields, **kwargs):
    if created or 'use_till' in update_fields:
        #initiate task to set status on expiration according to config
        try:
            config = Config.objects.get(created_by=instance.created_by)
            stockitem_expired_handler.apply_async(
                    ({'pk': instance.pk},), 
                    eta=instance.use_till-config.notify_on_expiration_before
                )
        except Exception as e:
            print(e)

    if created:
        try:
            handle_stock_change(instance, instance.volume)
        except Exception as e:
            print(e)

@receiver(pre_save, sender=StockItem)
def stockitem_status_handler(sender, instance, update_fields, **kwargs):
    if 'status' in update_fields and instance.status in [STOCK_STATUSES.COOKED, STOCK_STATUSES.WASTED]:
        handle_stock_change(instance, -instance.volume)
        instance.volume = 0

@receiver(post_save, sender=PurchaseItem)
def stockitem_handler(sender, instance, update_fields, **kwargs):
    if 'status' in update_fields and instance.status == PurchaseStatuses.BOUGHT:
        try:
            store_purchased_item(instance)
        except Exception as e:
            print(e)

@receiver(post_save, sender=CookingPlan)
def cookingplan_status_change_handler(sender, instance, update_fields, **kwargs):
    if 'status' in update_fields and instance.status == CookPlanStatuses.COOKED:
        try:
            handle_cooking_plan_fulfillment(instance)
        except Exception as e:
            print(e)

@receiver(post_save, Product)
def product_low_stock_handler(sender, instance, update_fields, **kwargs):
    if 'current_stock' in update_fields \
        and instance.minimal_stock_volume <= instance.current_stock:
        try:
            config = Config.objects.get(created_by=instance.created_by)
            # send notification
            if config.notify_on_min_stock:
                send_notification(instance, NotificationTypes.OUTAGE, config.notify_by_email)
            # try to generate shopping plan with auto generation is enabled
            if config.auto_generate_shopping_plan and config.gen_shop_plan_on_min_stock:
                generate_shopping_plan(config)
        except Exception as e:
            print(e)

@receiver(post_save, sender=Config)
def config_genshopplan_handler(sender, instance, created, update_fields, **kwargs):
    if created:
        if instance.gen_shop_plan_periodicity and instance.gen_shop_plan_periodicity > 0:
            schedule, schdl_created = IntervalSchedule.objects.get_or_create(
                                        every=instance.gen_shop_plan_periodicity,
                                        period=IntervalSchedule.DAYS,
                                    )
            #initiate task to repeatedly generate shopping plans
            try:
                PeriodicTask.objects.create(
                        interval=schedule,
                        name=f'{instance.created_by}-gen-shop-plan-repeat',
                        task='wgapi.tasks.repeat_shopping_plan_generator',
                        kwargs=json.dumps({'config': instance.pk,})
                    )
            except Exception as e:
                print(e)

    elif 'gen_shop_plan_repeatedly' in update_fields or 'gen_shop_plan_periodicity' in update_fields:
        if instance.gen_shop_plan_periodicity and instance.gen_shop_plan_periodicity:
            if instance.gen_shop_plan_periodicity > 0:
                schedule, schdl_created = IntervalSchedule.objects.get_or_create(
                                            every=instance.gen_shop_plan_periodicity,
                                            period=IntervalSchedule.DAYS,
                                        )
            #initiate task to repeatedly generate shopping plans
            try:
                # first try to update existing scheduled task if any
                existing_task = PeriodicTask.objects.get(
                        name=f'{instance.created_by}-gen-shop-plan-repeat'
                    )
                if existing_task:
                    if instance.gen_shop_plan_periodicity > 0:
                        existing_task.interval = schedule
                        existing_task.enabled = True
                    else:
                        existing_task.enabled = False
                    existing_task.save()
                # create new a scheduled task if not exist
                elif instance.gen_shop_plan_periodicity > 0:
                    PeriodicTask.objects.create(
                            interval=schedule,
                            name=f'{instance.created_by}-gen-shop-plan-repeat',
                            task='wgapi.tasks.repeat_shopping_plan_generator',
                            kwargs=json.dumps({'config': instance.pk,})
                        )
            except Exception as e:
                print(e)
