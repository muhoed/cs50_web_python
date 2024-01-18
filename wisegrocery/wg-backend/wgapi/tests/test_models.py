from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import *
from ..wg_enumeration import *


class WgModelTestCase(TestCase):
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
