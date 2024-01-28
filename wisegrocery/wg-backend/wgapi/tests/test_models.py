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


    def test_consumption_edit_quantity_increase_two_stock_items_with_equipment_without_overconsumption(self):
        """Asserts StockItem and Equipment records are modified when modifying existing Consumption to increase consumption quantity"""
        # create two equipment pieces with volume less than purchase quantity
        Equipment.objects.create(
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
            quantity=1.5,
            created_by=self.user
        )
        
        # get volumes of created stock items
        stock_items = StockItem.objects.all().order_by('created_on')
        volume1 = stock_items[0].volume
        volume2 = stock_items[1].volume
        eq1 = stock_items[0].equipment
        eq2 = stock_items[1].equipment

        consumption = Consumption.objects.create(
            product = self.test_prod,
            date = datetime.datetime.now().date(),
            type = ConsumptionTypes.OTHER,
            unit = test_purchase_item.unit,
            quantity = 0.4,
            created_by=self.user
        )

        # assert that volume of the first stock_item record was decreased by consumed quantity
        stock_items[0].refresh_from_db()
        self.assertEqual(stock_items[0].volume, round((Decimal(volume1)-Decimal(consumption.quantity)), 2))
        # save volume of first stock item for future use
        volume1 = stock_items[0].volume
        # assert that free space of the first equipment increased for correct value
        eq1.refresh_from_db()
        self.assertEqual(eq1.free_space, round(eq1.volume - volume1 / self.test_conv_rule_liter_to_kilogram.ratio, 2))

        # increase consumed quantity
        consumption.quantity = 1.2
        consumption.save(update_fields=['quantity'])

        # assert that only one stock item remained
        stock_items = StockItem.objects.all()
        self.assertEqual(stock_items.count(), 1)

        # assert that volume of stock_item record was decreased
        self.assertEqual(stock_items[0].volume, round(volume2-Decimal(1.2-0.4)+volume1, 2))
        # assert that the second equipment is empty and the first equipment free space is increased
        eq1.refresh_from_db()
        eq2.refresh_from_db()
        self.assertEqual(eq2.free_space, eq2.volume)
        self.assertEqual(eq1.free_space, round(eq1.volume-stock_items[0].volume / self.test_conv_rule_liter_to_kilogram.ratio, 2))


    def test_consumption_edit_quantity_increase_with_overconsumption(self):
        """Asserts StockItem and Equipment records are modified when modifying existing Consumption to increase consumption quantity"""
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

        consumption = Consumption.objects.create(
            product = self.test_prod,
            date = datetime.datetime.now().date(),
            type = ConsumptionTypes.OTHER,
            unit = test_purchase_item.unit,
            quantity = 0.4,
            created_by=self.user
        )

        with self.assertRaisesMessage(ValidationError, f'Stored quantity of the product can not be negative. Quantity is -{0.2}'):
            # increase consumed quantity
            consumption.quantity = 1.2
            consumption.save(update_fields=['quantity'])


    def test_consumption_edit_quantity_decrease_without_equipment(self):
        """Asserts new StockItem record created when modifying existing Consumption record to decrease consumed quantity without placing in equipment"""
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

        consumption = Consumption.objects.create(
            product = self.test_prod,
            date = datetime.datetime.now().date(),
            type = ConsumptionTypes.OTHER,
            unit = test_purchase_item.unit,
            quantity = 0.7,
            created_by=self.user
        )

        # assert that volume of stock_item record was decreased by consumed quantity
        stock_item = StockItem.objects.first()
        self.assertEqual(stock_item.volume, round(Decimal(1-0.7), 2))

        # decrease consumed quantity
        consumption.quantity = 0.5
        consumption.save(update_fields=['quantity'])

        # assert that volume of stock_item record wasn't changed
        stock_item.refresh_from_db()
        self.assertEqual(stock_item.volume, round(Decimal(1-0.7), 2))

        # assert new purchase was created
        purchases = Purchase.objects.all()
        self.assertEqual(purchases.count(), 2)
        # assert that new Purchase is of correct type and other attributes
        new_purchase = purchases.latest('created_on')
        self.assertEqual(new_purchase.type, PurchaseTypes.BALANCE)
        self.assertEqual(new_purchase.date, consumption.date)
        self.assertEqual(new_purchase.note, 'System purchase created to correct inventory balance due to reducing of quantity on an existing Consumption record.')

        # assert new purchase item was created
        purchase_items = PurchaseItem.objects.all()
        self.assertEqual(purchase_items.count(), 2)
        # assert that new Purchase Item has correct parameters
        new_purchase_item = purchase_items.latest('created_on')
        self.assertEqual(new_purchase_item.purchase, new_purchase)
        self.assertEqual(new_purchase_item.quantity, round(Decimal(0.7-0.5), 2))
        self.assertEqual(new_purchase_item.status, PurchaseStatuses.MOVED)
        self.assertEqual(new_purchase_item.use_till, stock_item.use_till)

        # assert that new stock_item record was created
        stock_items = StockItem.objects.all()
        self.assertEqual(stock_items.count(), 2)
        # assert that stock_item records were created with correct quantity
        self.assertEqual(stock_items.last().volume, round(Decimal(0.7-0.5), 2))


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


    def test_cooking_plan_fullfillment_with_overconsumption(self):
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
            volume=600,
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

        with self.assertRaisesMessage(ValidationError, f'Stored quantity of the product can not be negative. Quantity is -{round((2 * 600) - 1000, 2)}'):
            # change of CookingPlan status to fulfilled should trigger creation of Consumption instance
            test_cooking_plan.status = CookPlanStatuses.COOKED
            test_cooking_plan.save(update_fields=['status'])

