from django.apps import AppConfig


class WgapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wgapi'

    def ready(self):
        from . import signals
        from .models import EquipmentType, WiseGroceryUser
        from .wg_enumeration import BaseEquipmentTypes, BASE_EQUIPMENT_TEMPS, BASE_EQUIPMENT_ICONS

        try:
            sysuser = WiseGroceryUser.objects.get(username='sysuser')
            if not sysuser:
                raise Exception
        except:
            sysuser = WiseGroceryUser.objects.create(
                username = 'sysuser',
                email = 'sysuser@wisegrocery.com'
            )
            sysuser.set_password('SySUser&2022')
            sysuser.save()

        try:
            freezer = EquipmentType.objects.get(name='Freezer')
            if not freezer:
                raise Exception
        except:
            EquipmentType.objects.create(
                name = 'Freezer',
                description = 'Default equipment of type Freezer.',
                base_type = BaseEquipmentTypes.FREEZER,
                min_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.FREEZER.value][0],
                max_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.FREEZER.value][1],
                created_by = sysuser
            )
            EquipmentType.objects.create(
                name = 'Fridge',
                description = 'Default equipment of type Fridge.',
                base_type = BaseEquipmentTypes.FRIDGE,
                min_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.FRIDGE.value][0],
                max_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.FRIDGE.value][1],
                created_by = sysuser
            )
            EquipmentType.objects.create(
                name = 'Buffet',
                description = 'Default equipment of type Buffet.',
                base_type = BaseEquipmentTypes.BUFFET,
                min_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.BUFFET.value][0],
                max_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.BUFFET.value][1],
                created_by = sysuser
            )
            EquipmentType.objects.create(
                name = 'Cupboard',
                description = 'Default equipment of type Cupboard.',
                base_type = BaseEquipmentTypes.CUPBOARD,
                min_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.CUPBOARD.value][0],
                max_temp = BASE_EQUIPMENT_TEMPS[BaseEquipmentTypes.CUPBOARD.value][1],
                created_by = sysuser
            )
            