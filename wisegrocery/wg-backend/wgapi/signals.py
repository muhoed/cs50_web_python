import json

#from django_celery_beat.models import PeriodicTask, IntervalSchedule
#from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .helpers import *
from .models import Config, ConversionRule, CookingPlan, Product, PurchaseItem, StockItem, WiseGroceryUser
#from .tasks import stockitem_notify_expiration_handler, stockitem_expired_handler
from .wg_enumeration import STOCK_STATUSES, ConversionRuleTypes, CookPlanStatuses, NotificationTypes, PurchaseStatuses


@receiver(post_save, sender=WiseGroceryUser)
def wisegroceryuser_handler(sender, instance, created, **kwargs):
    if created:
        #create default config for a new user
        try:
            Config.objects.create(created_by=instance)
            print(f'Config for {instance.username} was created.')
        except Exception as e:
            print('Post-save user handler exception in create Config.')
            raise e

# @receiver(post_save, sender=StockItem)
# def stockitem_handler(sender, instance, created, update_fields, **kwargs):
#     if created or (update_fields and 'use_till' in update_fields):
#         #initiate task to set status on expiration according to config
#         try:
#             config = Config.objects.get(created_by=instance.created_by)
#             stockitem_notify_expiration_handler.apply_async(
#                     ({'pk': instance.pk},), 
#                     eta=instance.use_till-config.notify_on_expiration_before
#                 )
#             stockitem_expired_handler.apply_async(
#                     ({'pk': instance.pk},), 
#                     eta=instance.use_till
#                 )
#         except Exception as e:
#             print('StockItem post-save handler exception in stockitem_expired_handler.')
#             raise e

@receiver(post_save, sender=PurchaseItem)
def purchaseitem_handler(sender, instance, created, update_fields, **kwargs):
    if created and not update_fields:
        try:
            post_inventory(instance, instance.quantity)
        except Exception as e:
            print('PurchaseItem post-save handler exception in create')
            raise e
    if not created and update_fields and ('quantity' in update_fields or 'unit' in update_fields):
        try:
            update_inventory_record(instance)
        except Exception as e:
            print('PurchaseItem post-save handler exception in update')
            raise e

@receiver(post_save, sender=Consumption)
def consumption_handler(sender, instance, created, update_fields, **kwargs):
    if created and not update_fields:
        try:
            post_inventory(instance, instance.quantity)
                    
        except Exception as e:
            print(e)
            raise e
            
    if not created and (update_fields and ('quantity' in update_fields or 'unit' in update_fields)):
        try:
            update_inventory_record(instance)
        except Exception as e:
            print(e)
            raise e

@receiver(post_save, sender=CookingPlan)
def cookingplan_status_change_handler(sender, instance, update_fields, **kwargs):
    if update_fields and 'status' in update_fields and instance.status == CookPlanStatuses.COOKED:
        try:
            handle_cooking_plan_fulfillment(instance)
        except Exception as e:
            raise e

@receiver(post_save, sender=Product)
def product_post_save_handler(sender, instance, created, update_fields, **kwargs):
    if created:
        try:
            common_conv_rules = ConversionRule.objects.filter(type=ConversionRuleTypes.COMMON)
            for rule in common_conv_rules:
                if instance not in rule.products.all():
                    rule.products.add(instance)
                    rule.save()
        except Exception as e:
            print(e)
            raise e

# @receiver(post_save, sender=Config)
# def config_genshopplan_handler(sender, instance, created, update_fields, **kwargs):
#     if created:
#         if instance.gen_shop_plan_period and instance.gen_shop_plan_period > 0:
#             schedule, schdl_created = IntervalSchedule.objects.get_or_create(
#                                         every=instance.gen_shop_plan_period,
#                                         period=IntervalSchedule.DAYS,
#                                     )
#             #initiate task to repeatedly generate shopping plans
#             try:
#                 PeriodicTask.objects.create(
#                         interval=schedule,
#                         name=f'{instance.created_by}-gen-shop-plan-repeat',
#                         task='wgapi.tasks.repeat_shopping_plan_generator',
#                         kwargs=json.dumps({'config': instance.pk,})
#                     )
#             except Exception as e:
#                 print(e)

#     elif 'gen_shop_plan_repeatedly' in update_fields or 'gen_shop_plan_period' in update_fields:
#         if instance.gen_shop_plan_repeatedly and instance.gen_shop_plan_period:
#             if instance.gen_shop_plan_period > 0:
#                 schedule, schdl_created = IntervalSchedule.objects.get_or_create(
#                                             every=instance.gen_shop_plan_period,
#                                             period=IntervalSchedule.DAYS,
#                                         )
#             #initiate task to repeatedly generate shopping plans
#             try:
#                 # first try to update existing scheduled task if any
#                 existing_task = PeriodicTask.objects.get(
#                         name=f'{instance.created_by}-gen-shop-plan-repeat'
#                     )
#                 if existing_task:
#                     if instance.gen_shop_plan_period > 0:
#                         existing_task.interval = schedule
#                         existing_task.enabled = True
#                     else:
#                         existing_task.enabled = False
#                     existing_task.save()
#                 # create new a scheduled task if not exist
#                 elif instance.gen_shop_plan_period > 0:
#                     PeriodicTask.objects.create(
#                             interval=schedule,
#                             name=f'{instance.created_by}-gen-shop-plan-repeat',
#                             task='wgapi.tasks.repeat_shopping_plan_generator',
#                             kwargs=json.dumps({'config': instance.pk,})
#                         )
#             except Exception as e:
#                 print(e)
