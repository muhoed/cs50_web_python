from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.core.exceptions import ValidationError
from celery.contrib.testing.worker import start_worker


from ..models import *
from ..wg_enumeration import *
from wgbackend.celery import celery_app


class WgModelTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        start_worker(celery_app)
        
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
            ratio=1.03,
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
                       CELERY_ALWAYS_EAGER=True,
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
            created_by=self.user
        )
        Equipment.objects.create(
            name='TestEq2',
            description='Test equipment 2',
            type=self.test_eq_type,
            height=2,
            width=2,
            depth=2,
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
        self.assertEqual(stock_items[0].volume, eq1.volume * self.test_conv_rule_liter_to_kilogram)
        self.assertEqual(stock_items[1].volume, test_purchase_item.quantity - eq1.volume * self.test_conv_rule_liter_to_kilogram)
        # assert that purchase_item record status was changed to Stored
        test_purchase_item = PurchaseItem.objects.first()
        self.assertEqual(test_purchase_item.status, PurchaseStatuses.STORED)
        # assert Equipment available space was recalculated correctly
        equipments = Equipment.objects.all().order_by('created_on')
        self.assertEqual(equipments[0].free_space, 0)
        self.assertEqual(equipments[1].free_space, equipments[1].volume - stock_items[1].volume / self.test_conv_rule_liter_to_kilogram)

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
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
