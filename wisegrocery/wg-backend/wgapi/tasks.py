# start worker 'celery -A wgbackend worker -l INFO'
#from wgbackend.celery import app as celery_app
import datetime
from celery import shared_task


def import_django_instance():
    """
    Makes django environment available 
    to tasks!!
    Credits to Raihan Kabir. See 'https://stackoverflow.com/questions/66160524/django-model-object-as-parameter-for-celery-task-raises-encodeerror-object-of'
    """
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wgbackend.settings')
    django.setup()


@shared_task
def stockitem_notify_expiration_handler(): #(data):
	try:
		import_django_instance()
		from django.utils.translation import gettext_lazy as _
		from wgapi.models import Config, StockItem
		from wgapi.helpers import send_notification
		from wgapi.wg_enumeration import NotificationTypes, STOCK_STATUSES
		
		#instance = StockItem.objects.get(pk=int(data.get('pk')))
		#config = Config.objects.get(created_by=instance.created_by)
		configs = Config.objects.all()
		for config in configs:
			if config.notify_on_expiration:
				stock_items = StockItem.objects.filter(
					status__in=[STOCK_STATUSES.ACTIVE, STOCK_STATUSES.NOTPLACED],
					use_till=datetime.datetime.now().date()+config.notify_on_expiration_before,
					created_by=config.created_by
				)
				for stock_item in stock_items:
					send_notification(stock_item, NotificationTypes.BEFOREXPIRATION, config.notify_by_email)
		# if config.notify_on_expiration:
		# 	send_notification(instance, NotificationTypes.BEFOREXPIRATION, config.notify_by_email)

	except Exception as e:
		print(e)
		raise e


@shared_task
def stockitem_expired_handler(): #(data):
	try:
		import_django_instance()
		from django.utils.translation import gettext_lazy as _
		from wgapi.models import Config, StockItem, Consumption
		from wgapi.helpers import send_notification
		from wgapi.wg_enumeration import STOCK_STATUSES, EXPIRED_ACTIONS, NotificationTypes, ConsumptionTypes
		
		# instance = StockItem.objects.get(pk=int(data.get('pk')))
		# config = Config.objects.get(created_by=instance.created_by)
		print('expiration')
		configs = Config.objects.all()
		for config in configs:
			stock_items = StockItem.objects.filter(
				status__in=[STOCK_STATUSES.ACTIVE, STOCK_STATUSES.NOTPLACED],
				use_till=datetime.datetime.now().date(),
				created_by=config.created_by
			)
			for stock_item in stock_items:
				if config.default_expired_action == EXPIRED_ACTIONS.TRASH:
					# first change status of stock item to Trashed for further pairing
					stock_item.status = STOCK_STATUSES.TRASHED
					stock_item.save()
					# create Consumption record of respective type
					# stock_item deletion will be triggered by Consumption post_save signal 
					Consumption.objects.create(
						product = stock_item.purchase_item.product,
						date = stock_item.use_till,
						type = ConsumptionTypes.TRASHED,
						unit = stock_item.unit,
						quantity = stock_item.volume,
						created_by=stock_item.created_by
					)
				else:
					# prolong if allowed
					if config.default_expired_action == EXPIRED_ACTIONS.PROLONG:
						stock_item.use_till += config.prolong_expired_for
					# otherwise mark as expired 
					else:
						stock_item.status = STOCK_STATUSES.EXPIRED
						if config.notify_on_expiration:
							send_notification(stock_item, NotificationTypes.EXPIRATION, config.notify_by_email)
					stock_item.save()

	except Exception as e:
		print(e)
		raise e

# @shared_task
# def repeat_shopping_plan_generator(data):
# 	try:
# 		import_django_instance()
# 		from wgapi.models import Config
# 		from wgapi.helpers import generate_shopping_plan

# 		config = Config.objects.get(pk=data['config'])
# 		generate_shopping_plan(config)
# 	except Exception as e:
# 		print(e)

