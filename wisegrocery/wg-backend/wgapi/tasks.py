# start worker 'celery -A wgbackend worker -l INFO'
#from wgbackend.celery import app as celery_app
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
def stockitem_expired_handler(data):
	try:
		import_django_instance()
		from django.utils.translation import gettext_lazy as _
		from wgapi.models import Config, StockItem, Consumption
		from wgapi.helpers import send_notification
		from wgapi.wg_enumeration import STOCK_STATUSES, EXPIRED_ACTIONS, NotificationTypes, ConsumptionTypes
		
		instance = StockItem.objects.get(pk=int(data.get('pk')))
		config = Config.objects.get(created_by=instance.created_by)
		if config.default_expired_action == EXPIRED_ACTIONS.TRASH:
			# create Consumption record of respective type
			# stock_item deletion will be triggered by Consumption post_save signal 
			Consumption.object.create(
				product = instance.product,
				stock_item = instance,
				date = instance.use_till,
				type = ConsumptionTypes.TRASHED,
				unit = instance.unit,
				quantity = instance.volume
			)
		else:
			# prolong if allowed
			if config.default_expired_action == EXPIRED_ACTIONS.PROLONG:
				instance.use_till += config.prolong_expired_for
			# otherwise mark as expired 
			else:
				instance.status = STOCK_STATUSES.EXPIRED
				if config.notify_on_expiration:
					send_notification(instance, NotificationTypes.EXPIRATION, config.notify_by_email)
			instance.save()

	except instance.DoesNotExist as e1:
		print(e1)

	except config.DoesNotExist as e2:
		print(e2)

	except Exception as e3:
		print(e3)

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

