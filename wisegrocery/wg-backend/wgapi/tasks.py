# start worker 'celery -A commerce worker -l INFO'
#from commerce.celery import app as celery_app
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
		from wgapi.models import StockItem
		from wgapi.wg_enumeration import STOCK_STATUSES
		
		instance = StockItem.objects.get(pk=int(data.get('pk')))
		instance.status = STOCK_STATUSES.EXPIRED
		instance.save()

	except instance.DoesNotExist as e:
		print(e)
