from django.test import TestCase

from ..models import *
from ..shopping import *
from ..wg_enumeration import *


class WgShoppingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = WiseGroceryUser.objects.create(
            username='TestUser',
            email='TestUser@email.com'
        )
        cls.user.set_password('Test')
        cls.user.save()

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
            ratio=Decimal(1.03),
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

        cls.test_prod1 = Product.objects.create(
            name='Banana',
            description='Test banana',
            category=ProductCategories.FRUITS,
            minimal_stock_volume=1,
            unit=VolumeUnits.KILOGRAM,
            min_tempreture=5,
            max_tempreture=35,
            created_by=cls.user
        )

        cls.test_prod2 = Product.objects.create(
            name='Milk',
            description='Test milk',
            category=ProductCategories.DRINKS,
            minimal_stock_volume=2,
            unit=VolumeUnits.LITER,
            min_tempreture=8,
            max_tempreture=12,
            created_by=cls.user
        )

        cls.test_recipe = Recipe.objects.create(
            name='Test recipe',
            description='Test recipe description',
            num_persons=2,
            cooking_time=datetime.timedelta(hours=1),
            created_by=cls.user
        )
        cls.test_recipe_product1 = RecipeProduct.objects.create(
            recipe=cls.test_recipe,
            product=cls.test_prod1,
            unit=VolumeUnits.GRAM,
            volume=600,
            created_by=cls.user
        )
        cls.test_recipe_product2 = RecipeProduct.objects.create(
            recipe=cls.test_recipe,
            product=cls.test_prod2,
            unit=VolumeUnits.GRAM,
            volume=Decimal(0.3),
            created_by=cls.user
        )
        
        cls.test_cooking_plan = CookingPlan.objects.create(
            date=datetime.datetime.now(),
            meal=Meals.DINNER,
            persons=4,
            created_by=cls.user
        )
        cls.test_cooking_plan.recipes.add(cls.test_recipe)
        cls.test_cooking_plan.save()

        cls.test_shopping = Shopping(cls.user.pk)

    def test_get_open_cooking_plans(self):
        """ Asserts get_open_cooking_plans method returns correct cooking plan instances """

        new_cooking_plan = CookingPlan.objects.create(
            date=datetime.datetime.now(),
            meal=Meals.LUNCH,
            persons=3,
            created_by=self.user
        )
        new_cooking_plan.recipes.add(self.test_recipe)
        new_cooking_plan.save()

        # assert that initial number of open cooking plans returned by method is two
        self.assertEqual(self.test_shopping.get_open_cooking_plans().count(), 2)

        # fulfill one of the cooking plan and re-assert
        new_cooking_plan.status = CookPlanStatuses.COOKED
        new_cooking_plan.save()
        self.assertEqual(self.test_shopping.get_open_cooking_plans().count(), 1)