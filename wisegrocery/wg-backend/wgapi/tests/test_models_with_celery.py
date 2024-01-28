from decimal import Decimal
from threading import Thread
import time
from django.test import TransactionTestCase
from django.test.utils import override_settings
from celery.contrib.testing.worker import start_worker
from celery.apps.beat import Beat


from ..models import *
from ..wg_enumeration import *
from wgbackend.celery import celery_app


class WgModelTestCase(TransactionTestCase):
    def setUp(self):
        user = WiseGroceryUser.objects.create(
            username='TestUser',
            email='TestUser@email.com'
        )
        user.set_password('Test')
        user.save()

        self.user = user

        self.test_eq_type = EquipmentType.objects.create(
            name='Test',
            description='Test equipment type',
            base_type = BaseEquipmentTypes.BUFFET,
            created_by=self.user
        )

        self.test_conv_rule_liter_to_gram = ConversionRule.objects.create(
            name='Liter to gram rule',
            type=ConversionRuleTypes.COMMON,
            from_unit=VolumeUnits.LITER,
            to_unit=VolumeUnits.GRAM,
            ratio=1030,
            created_by=self.user
        )

        self.test_conv_rule_liter_to_kilogram = ConversionRule.objects.create(
            name='Liter to kilogram rule',
            type=ConversionRuleTypes.COMMON,
            from_unit=VolumeUnits.LITER,
            to_unit=VolumeUnits.KILOGRAM,
            ratio=Decimal(1.03),
            created_by=self.user
        )

        self.test_conv_rule = ConversionRule.objects.create(
            name='Test rule',
            type=ConversionRuleTypes.COMMON,
            from_unit=VolumeUnits.GRAM,
            to_unit=VolumeUnits.KILOGRAM,
            ratio=1000,
            created_by=self.user
        )

        self.test_prod = Product.objects.create(
            name='Test',
            description='Test product',
            category=ProductCategories.FRUITS,
            minimal_stock_volume=1,
            unit=VolumeUnits.KILOGRAM,
            min_tempreture=10,
            max_tempreture=20,
            created_by=self.user
        )

    def run_celery_worker(self):
        start_worker(app=celery_app, loglevel='error')

    def run_celery_beat_helper(self):
        beat = Beat(app=celery_app, loglevel='error', quiet=True)
        beat.run()


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_TASK_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://",
                       CELERY_BEAT_SCHEDULE = {
                            'expiration_handling': {
                                'task': 'wgapi.tasks.stockitem_expired_handler',
                                'schedule': 2.0,
                            },
                       })
    def test_stock_item_trashed_on_expiration(self):
        """Asserts StockItem record deleted and Cunsumption record of type TRASHED created on stock item expiration"""

        p1 = Thread(target=self.run_celery_beat_helper, daemon=True)
        p2 = Thread(target=self.run_celery_worker, daemon=True)
        p1.start()
        p2.start()
        
        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        use_till = test_purchase.date + datetime.timedelta(days=1)
        PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            use_till=use_till,
            created_by=self.user
        )

        time.sleep(2)

        # assert that no StockItem exists
        stock_items = StockItem.objects.all()
        self.assertEqual(stock_items.count(), 0)
        # assert that Consumption record is created and has correct quantity and status
        consumptions = Consumption.objects.all()
        self.assertEqual(consumptions.count(), 1)
        self.assertEqual(consumptions[0].quantity, 1)
        self.assertEqual(consumptions[0].type, ConsumptionTypes.TRASHED)


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_TASK_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://",
                       CELERY_BEAT_SCHEDULE = {
                            'expiration_handling': {
                                'task': 'wgapi.tasks.stockitem_expired_handler',
                                'schedule': 2.0,
                            },
                       })
    def test_stock_item_prolonged_on_expiration(self):
        """Asserts StockItem record usage period prolonged on stock item expiration when Prolong on expiration Config setting is enabled"""
        
        p1 = Thread(target=self.run_celery_beat_helper, daemon=True)
        p2 = Thread(target=self.run_celery_worker, daemon=True)
        p1.start()
        p2.start()

        config = Config.objects.get(created_by=self.user)
        config.default_expired_action = EXPIRED_ACTIONS.PROLONG
        config.save()

        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        use_till = test_purchase.date + datetime.timedelta(days=1)
        purch_item = PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            use_till=use_till,
            created_by=self.user
        )

        time.sleep(2)

        # assert that StockItem use_till increased for 7 days (default value) and its status not changed 
        stock_item_prolonged = StockItem.objects.first()
        new_use_till = purch_item.use_till + config.prolong_expired_for
        self.assertEqual(stock_item_prolonged.use_till, new_use_till.date())
        self.assertEqual(stock_item_prolonged.status, STOCK_STATUSES.NOTPLACED.value)


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_TASK_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://",
                       CELERY_BEAT_SCHEDULE = {
                            'expiration_handling': {
                                'task': 'wgapi.tasks.stockitem_expired_handler',
                                'schedule': 2.0,
                            },
                       })
    def test_stock_item_set_to_expired_on_expiration(self):
        """Asserts StockItem record status changed to Expired on stock item expiration when default expiration action in Config setting is Allow"""
        
        p1 = Thread(target=self.run_celery_beat_helper, daemon=True)
        p2 = Thread(target=self.run_celery_worker, daemon=True)
        p1.start()
        p2.start()

        config = Config.objects.get(created_by=self.user)
        config.default_expired_action = EXPIRED_ACTIONS.ALLOW
        config.save()

        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        use_till = test_purchase.date + datetime.timedelta(days=1)
        PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            use_till=use_till,
            created_by=self.user
        )

        time.sleep(2)

        # assert that StockItem status changed to Expired 
        stock_item = StockItem.objects.first()
        self.assertEqual(stock_item.status, STOCK_STATUSES.EXPIRED.value)
