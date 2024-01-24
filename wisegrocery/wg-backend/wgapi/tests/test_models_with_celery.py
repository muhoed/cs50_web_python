from decimal import Decimal
import time
from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.core.exceptions import ValidationError
from celery.contrib.testing.worker import start_worker
from celery.apps.beat import Beat


from ..models import *
from ..wg_enumeration import *
from wgbackend.celery import celery_app


class WgModelTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        start_worker(celery_app)
        # beat = Beat(app=celery_app, loglevel='warning', quiet=True)
        # beat.run()
        
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


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_purchase_item_posted_to_inventory_and_stored(self):
        """Asserts StoskItem records are created from PurchaseItem and stored in available equipment"""
        # we need equipments to store stock of products
        # create two equipment pieces with volume less than purchase quantity
        eq1 = Equipment.objects.create(
            name='TestEq1',
            description='Test equipment 1',
            type=self.test_eq_type,
            height=2,
            width=2,
            depth=2,
            min_tempreture=15,
            max_tempreture=18,
            rated_size=1,
            created_by=self.user
        )
        Equipment.objects.create(
            name='TestEq2',
            description='Test equipment 2',
            type=self.test_eq_type,
            height=2,
            width=2,
            depth=2,
            min_tempreture=15,
            max_tempreture=18,
            rated_size=1,
            created_by=self.user
        )

        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        test_purchase_item = PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            created_by=self.user
        )

        # assert that two stock_item record was created
        stock_items = StockItem.objects.all().order_by('created_on')
        self.assertEqual(stock_items.count(), 2)
        # assert that stock_item records were created with correct quantity
        self.assertEqual(stock_items[0].volume, round(eq1.volume * self.test_conv_rule_liter_to_kilogram.ratio, 2))
        self.assertEqual(stock_items[1].volume, round(test_purchase_item.quantity - eq1.volume * self.test_conv_rule_liter_to_kilogram.ratio, 2))
        # assert that purchase_item record status was changed to Stored
        test_purchase_item = PurchaseItem.objects.first()
        self.assertEqual(test_purchase_item.status, PurchaseStatuses.STORED)
        # assert Equipment available space was recalculated correctly
        equipments = Equipment.objects.all().order_by('free_space')
        self.assertEqual(equipments[0].free_space, 0)
        self.assertEqual(equipments[1].free_space, round(equipments[1].volume - stock_items[1].volume / self.test_conv_rule_liter_to_kilogram.ratio, 2))


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_purchase_item_posted_to_inventory_and_partially_stored(self):
        """Asserts StoskItem records are created from PurchaseItem and partially stored in available equipment"""
        # we need equipment to partially store stock of products
        eq1 = Equipment.objects.create(
            name='TestEq1',
            description='Test equipment 1',
            type=self.test_eq_type,
            height=2,
            width=2,
            depth=2,
            min_tempreture=15,
            max_tempreture=18,
            rated_size=1,
            created_by=self.user
        )

        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        test_purchase_item = PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            created_by=self.user
        )

        # assert that two stock_item record was created
        stock_items = StockItem.objects.all().order_by('created_on')
        self.assertEqual(stock_items.count(), 2)
        # assert that stock_item records were created with correct quantity
        self.assertEqual(stock_items[0].volume, round(eq1.volume * self.test_conv_rule_liter_to_kilogram.ratio, 2))
        self.assertEqual(stock_items[1].volume, round(test_purchase_item.quantity - eq1.volume * self.test_conv_rule_liter_to_kilogram.ratio, 2))
        # assert that purchase_item record status was changed to Partially Stored
        test_purchase_item = PurchaseItem.objects.first()
        self.assertEqual(test_purchase_item.status, PurchaseStatuses.PARTIALLY_STORED)
        # assert Equipment available space was recalculated correctly
        eq1 = Equipment.objects.first()
        self.assertEqual(eq1.free_space, 0)


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_purchase_item_posted_to_inventory_and_not_stored(self):
        """Asserts StoskItem records are created from PurchaseItem and stayed in not stored status"""
        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        test_purchase_item = PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            created_by=self.user
        )

        # assert that only one stock_item record was created
        stock_items = StockItem.objects.all()
        self.assertEqual(stock_items.count(), 1)
        # assert that stock_item records were created with correct quantity
        self.assertEqual(stock_items.first().volume, 1)
        # assert that stock_item records status is Not Placed
        self.assertEqual(stock_items.first().status, STOCK_STATUSES.NOTPLACED)
        # assert that purchase_item record status remained Bought
        test_purchase_item = PurchaseItem.objects.first()
        self.assertEqual(test_purchase_item.status, PurchaseStatuses.BOUGHT)


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_purchase_item_edit_quantity_increase(self):
        """Asserts new StockItem record is created when modifying existing PutchaseItem to increase quantity"""
        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        test_purchase_item = PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            created_by=self.user
        )

        test_purchase_item.quantity = 1.2
        test_purchase_item.save(update_fields=['quantity'])

        # assert that the second stock_item record was created
        stock_items = StockItem.objects.all().order_by('created_on')
        self.assertEqual(stock_items.count(), 2)
        # assert that stock_item records were created with correct quantity
        self.assertEqual(stock_items[0].volume, 1)
        self.assertEqual(stock_items[1].volume, round(Decimal(0.2), 2))


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_purchase_item_edit_quantity_decrease_without_equipment(self):
        """Asserts StockItem record volume decreased when modifying existing PutchaseItem to decrease quantity"""
        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        test_purchase_item = PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            created_by=self.user
        )

        test_purchase_item.quantity = 0.8
        test_purchase_item.save(update_fields=['quantity'])

        # assert that still only one StockItem instance
        stock_items = StockItem.objects.all()
        self.assertEqual(stock_items.count(), 1)
        # assert that stock_item record quantity was decreased
        self.assertEqual(stock_items[0].volume, round(Decimal(0.8), 2))


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_purchase_item_edit_quantity_decrease_with_two_equipment_of_enough_capacity(self):
        """Asserts StockItem record deleted and volume decreased when modifying existing PutchaseItem to decrease quantity while storing in two equipments"""
        # create two equipment pieces with volume less than purchase quantity
        eq1 = Equipment.objects.create(
            name='TestEq1',
            description='Test equipment 1',
            type=self.test_eq_type,
            height=2,
            width=2,
            depth=2,
            min_tempreture=15,
            max_tempreture=18,
            rated_size=1,
            created_by=self.user
        )
        eq2 = Equipment.objects.create(
            name='TestEq2',
            description='Test equipment 2',
            type=self.test_eq_type,
            height=2,
            width=2,
            depth=2,
            min_tempreture=15,
            max_tempreture=18,
            rated_size=1,
            created_by=self.user
        )
        
        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        test_purchase_item = PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            created_by=self.user
        )

        # get initial stock items quantities
        stock_items = StockItem.objects.all().order_by('created_on')
        first_stock_item_vol = stock_items[0].volume
        second_stock_item_vol = stock_items[1].volume

        test_purchase_item.quantity = 0.5
        test_purchase_item.save(update_fields=['quantity'])

        # assert that only one StockItem instance remained
        stock_items = StockItem.objects.all()
        self.assertEqual(stock_items.count(), 1)
        # assert that stock_item record quantity was decreased
        self.assertEqual(stock_items[0].volume, round(first_stock_item_vol - (Decimal(0.5) - second_stock_item_vol), 2))
        # assert that free space of the second equipment is equal to its volume
        eq2.refresh_from_db()
        self.assertEqual(eq2.volume, eq2.free_space)
        # assert that free space of the first equipment increased for correct value
        eq1.refresh_from_db()
        self.assertEqual(eq1.free_space, round(eq1.volume - stock_items[0].volume / self.test_conv_rule_liter_to_kilogram.ratio, 2))


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_TASK_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_stock_item_trashed_on_expiration(self):
        """Asserts StockItem record deleted and Cunsumption record of type TRASHED created on stock item expiration"""
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
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_stock_item_prolonged_on_expiration(self):
        """Asserts StockItem record usage period prolonged on stock item expiration when Prolong on expiration Config setting is enabled"""
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

        # assert that StockItem use_till increased for 7 days (default value) and its status not changed 
        stock_item_prolonged = StockItem.objects.first()
        new_use_till = purch_item.use_till + config.prolong_expired_for
        self.assertEqual(stock_item_prolonged.use_till, new_use_till.date())
        self.assertEqual(stock_item_prolonged.status, STOCK_STATUSES.NOTPLACED.value)


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_TASK_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_stock_item_set_to_expired_on_expiration(self):
        """Asserts StockItem record status changed to Expired on stock item expiration when default expiration action in Config setting is Allow"""
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

        # assert that StockItem status changed to Expired 
        stock_item = StockItem.objects.first()
        self.assertEqual(stock_item.status, STOCK_STATUSES.EXPIRED.value)


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       #CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://",
                       CELERY_RESULT_BACKEND = "rpc://")
    def test_cooking_plan_fullfillment(self):
        """Asserts Consumption record is created on Cooking plan """
        # we need equipment to store stock of products
        Equipment.objects.create(
            name='Test',
            description='Test equipment',
            type=self.test_eq_type,
            height=50,
            width=80,
            depth=40,
            created_by=self.user
        )

        test_recipe = Recipe.objects.create(
            name='Test recipe',
            description='Test recipe description',
            num_persons=2,
            cooking_time=datetime.timedelta(hours=1),
            created_by=self.user
        )
        test_recipe_product = RecipeProduct(
            recipe=test_recipe,
            product=self.test_prod,
            unit=VolumeUnits.GRAM,
            volume=150,
            created_by=self.user
        )
        test_recipe_product.save()
        test_cooking_plan = CookingPlan.objects.create(
            date=datetime.datetime.now(),
            meal=Meals.DINNER,
            persons=4,
            created_by=self.user
        )
        test_cooking_plan.recipes.add(test_recipe)
        test_cooking_plan.save()
        # we need to create StockItem to consume. to create it, we need to create Purchase and PurchaseItem first
        test_purchase = Purchase.objects.create(
            date=datetime.datetime.now() - datetime.timedelta(days=1),
            type=PurchaseTypes.BALANCE,
            created_by=self.user
        )
        PurchaseItem.objects.create(
            purchase=test_purchase,
            product=self.test_prod,
            unit=self.test_prod.unit,
            quantity=1,
            created_by=self.user
        )

        # change of CookingPlan status to fulfilled should trigger creation of Consumption instance
        test_cooking_plan.status = CookPlanStatuses.COOKED
        test_cooking_plan.save(update_fields=['status'])

        consumptions = Consumption.objects.all()
        stock_items = StockItem.objects.all()

        # assert that only one consumption record was created
        self.assertEqual(consumptions.count(), 1)
        # assert that consumption record was created with correct quantity
        consumption = consumptions.first()
        self.assertEqual(consumption.quantity, 150 / 2 * 4)
        # assert that stock was reduced for correct quantity
        stock_item = stock_items.first()
        self.assertEqual(stock_item.volume, 1 - (consumption.quantity / 1000))
