from django.test import TestCase
from django.test.utils import override_settings
from django.core.exceptions import ValidationError
from celery.contrib.testing.worker import start_worker


from ..models import *
from ..wg_enumeration import *
#from ...wgbackend.celery import celery_app


class WgModelTestCase(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     super().setUpClass()
    #     cls.celery_worker = start_worker(celery_app)
    #     cls.celery_worker.__enter__()

    # @classmethod
    # def tearDownClass(cls):
    #     super().tearDownClass()
    #     cls.celery_worker.__exit__(None, None, None)

    @classmethod
    def setUpTestData(cls):
        cls.user = WiseGroceryUser.objects.create(
            username='TestUser',
            email='TestUser@email.com'
        )
        cls.user.set_password('Test')
        cls.user.save()

        cls.test_eq_type = EquipmentType.objects.create(
            name='Test',
            description='Test equipment type',
            base_type = BaseEquipmentTypes.BUFFET,
            created_by=cls.user
        )

        cls.test_conv_rule_liter_to_gram = ConversionRule.objects.create(
            name='Liter to gram rule',
            type=ConversionRuleTypes.COMMON,
            from_unit=VolumeUnits.LITER,
            to_unit=VolumeUnits.GRAM,
            ratio=1030,
            created_by=cls.user
        )

        cls.test_conv_rule_liter_to_kilogram = ConversionRule.objects.create(
            name='Liter to kilogram rule',
            type=ConversionRuleTypes.COMMON,
            from_unit=VolumeUnits.LITER,
            to_unit=VolumeUnits.KILOGRAM,
            ratio=1.03,
            created_by=cls.user
        )

        cls.test_conv_rule = ConversionRule.objects.create(
            name='Test rule',
            type=ConversionRuleTypes.COMMON,
            from_unit=VolumeUnits.GRAM,
            to_unit=VolumeUnits.KILOGRAM,
            ratio=1000,
            created_by=cls.user
        )

        cls.test_prod = Product.objects.create(
            name='Test',
            description='Test product',
            category=ProductCategories.FRUITS,
            minimal_stock_volume=1,
            unit=VolumeUnits.KILOGRAM,
            min_tempreture=10,
            max_tempreture=20,
            created_by=cls.user
        )

    def test_user_config(self):
        """Asserts config was creted for a new user"""

        self.assertIn(Config.objects.get(created_by=self.user), Config.objects.all())

    def test_equipment_type_temps(self):
        """Asserts correct default configuration of Equipment type minimal and maximum tempertures"""

        self.assertEqual(self.test_eq_type.min_temp, 15)
        self.assertEqual(self.test_eq_type.max_temp, 25)

    def test_equipment(self):
        """Asserts correct default configuration of Equipment parameters"""
        test_eq = Equipment.objects.create(
            name='Test',
            description='Test equipment',
            type=self.test_eq_type,
            height=50,
            width=80,
            depth=40,
            created_by=self.user
        )

        self.assertEqual(test_eq.volume, ((50 * 80 * 40) / 10) * 0.85)
        self.assertEqual(test_eq.free_space, ((50 * 80 * 40) / 10) * 0.85)
        self.assertEqual(test_eq.min_tempreture, 15)
        self.assertEqual(test_eq.max_tempreture, 25)
        
    def test_save_product(self):
        """Asserts correct default configuration of Product picture path"""
        self.assertEqual(self.test_prod.picture.name, 'icons/product/fruits.png')

    def test_product_added_to_conv_rule(self):
        """Asserts product is linked to a common conversion rule"""
        added_products = self.test_conv_rule.products
        self.assertEqual(added_products.count(), 1)

        added_product = added_products.first()
        self.assertEqual(added_product, self.test_prod)

    def test_conv_rules_unit_from_to_validation(self):
        """Asserts validation error is raised if conversion rule From unit is equal to To unit"""
        with self.assertRaisesMessage(ValidationError, "From_Unit and To_Unit can not be the same."):
            ConversionRule.objects.create(
                name='Test rule 1',
                type=ConversionRuleTypes.COMMON,
                from_unit=VolumeUnits.GRAM,
                to_unit=VolumeUnits.GRAM,
                ratio=1000,
                created_by=self.user
            )

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       CELERY_BROKER_URL = "memory://")
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
