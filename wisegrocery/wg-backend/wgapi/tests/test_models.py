from django.test import TestCase

from ..models import *
from ..wg_enumeration import *


class WgTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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


class EquipmentTypeTestCase(WgTestCase):

    def test_equipment_type_temps(self):
        """Asserts correct default configuration of Equipment type minimal and maximum tempertures"""

        self.assertEqual(self.test_eq_type.min_temp, 15)
        self.assertEqual(self.test_eq_type.max_temp, 25)


class EquipmentTestCase(WgTestCase):
    def setUp(self):
        Equipment.objects.create(
            name='Test',
            description='Test equipment',
            type=self.test_eq_type,
            height=50,
            width=80,
            depth=40,
            created_by=self.user
        )

    def test_equipment(self):
        """Asserts correct default configuration of Equipment parameters"""
        test_eq = Equipment.objects.get(name='Test')

        self.assertEqual(test_eq.volume, ((50 * 80 * 40) / 10) * 0.85)
        self.assertEqual(test_eq.free_space, ((50 * 80 * 40) / 10) * 0.85)
        self.assertEqual(test_eq.min_tempreture, 15)
        self.assertEqual(test_eq.max_tempreture, 25)
