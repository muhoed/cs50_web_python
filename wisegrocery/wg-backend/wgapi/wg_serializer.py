from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers as rest_serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import *
from .relations import *


class PartialUpdateModelSerializer(rest_serializers.ModelSerializer):
    """
    Make use of update_fields while saving updated instance.
    Lets catch update_fields in post_save signal.
    """

    def update(self, instance, validated_data):
        rest_serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = rest_serializers.model_meta.get_field_info(instance)
        _updated_fields = []

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
                _updated_fields.append(attr)

        instance.save(update_fields=_updated_fields)

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

class WGTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        return token


class RegisterSerializer(rest_serializers.ModelSerializer):
    password1 = rest_serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = rest_serializers.CharField(write_only=True, required=True)
    email = rest_serializers.EmailField()

    class Meta:
        model = WiseGroceryUser
        fields = ('username', 'email', 'password1', 'password2')

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise rest_serializers.ValidationError(
                {"password2": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = WiseGroceryUser.objects.create(
            username=validated_data['username'],
            email = validated_data['email']
        )

        user.set_password(validated_data['password1'])
        user.save()

        return user

class EquipmentSerializer(PartialUpdateModelSerializer):
    stockitem_set = StockItemSetField(many=True, read_only=True)
    class Meta:
        model = Equipment
        fields = [
            'name', 'description', 'type', 'icon', 'height', 'width', 'depth', 'volume', 
            'rated_size', 'free_space', 'min_tempreture', 'max_tempreture', 'stockitem_set', 
            'created_on', 'updated_on'
            ]
        read_only_fields = ['free_space', 'created_on', 'updated_on']
        depth = 1

class EquipmentTypeSerializer(PartialUpdateModelSerializer):
    equipment_set = EquipmentSetField(many=True, read_only=True)

    class Meta:
        model = EquipmentType
        fields = [
            'name', 'description', 'base_type', 'min_temp', 'max_temp', 'equipment_set',
            'created_on', 'updated_on'
            ]
        read_only_fields = ['equipment_set', 'created_on', 'updated_on']

class ProductSerializer(PartialUpdateModelSerializer):
    replacement_products = ReplacementProductsField(many=True, read_only=True)
    recipeproduct_set = RecipeProductField(many=True, read_only=True)
    conversionrule_set = ConversionRuleSetField(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'supplier', 'picture', 
            'minimal_stock_volume', 'unit', 'current_stock', 'alternative_to', 
            'replacement_products', 'recipeproduct_set', 'conversionrule_set',
            'min_tempreture', 'max_tempreture', 'created_on', 'updated_on'
        ]
        read_only_fields = ['current_stock', 'created_on', 'updated_on']
        depth = 1

class StockItemSerializer(PartialUpdateModelSerializer):
    class Meta:
        model = StockItem
        fields = [
            'product', 'equipment', 'unit', 'volume', 'initial_volume', 'use_till', 
            'status', 'created_on', 'updated_on'
        ]
        read_only_fields = ['initial_volume', 'created_on', 'updated_on']
        depth = 1

class RecipeSerializer(PartialUpdateModelSerializer):
    items = RecipeProductField(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'name', 'description', 'items', 'num_persons', 'cookingplan_set',
            'recipeproduct_set', 'cooking_time', 'created_on', 'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class RecipeProductSerializer(PartialUpdateModelSerializer):
    class Meta:
        model = RecipeProduct
        fields = ['recipe', 'product', 'unit', 'volume', 'created_on', 'updated_on']
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class CookingPlanSerializer(PartialUpdateModelSerializer):
    class Meta:
        model = CookingPlan
        fields = ['date', 'meal', 'persons', 'recipe', 'note', 'created_on', 'updated_on']
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class PurchaseSerializer(PartialUpdateModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            'date', 'type', 'store', 'total_amount', 'note', 'created_on', 
            'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class PurchaseItemSerializer(PartialUpdateModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = [
            'purchase', 'product', 'unit', 'quantity', 'price', 'status', 'created_on', 
            'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

# class ShoppingPlanSerializer(PartialUpdateModelSerializer):
#     class Meta:
#         model = ShoppingPlan
#         fields = ['date', 'note', 'purchaseitem_set', 'status', 'created_on', 'updated_on']
#         read_only_fields = ['created_on', 'updated_on']
#         depth = 1

class ConsumptionSerializer(PartialUpdateModelSerializer):
    stock_items = StockItemSetField(many=True, read_only=True)
    class Meta:
        model = Consumption
        fields = [
            'product', 'cooking_plan', 'recipe_product', 'stock_items', 'date', 'typy', 'unit', 'quantity', 
            'note', 'created_on', 'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class ConversionRuleSerializer(PartialUpdateModelSerializer):
    products = ConversionRuleProductSetField(many=True, read_only=True)
    class Meta:
        model = ConversionRule
        fields = [
            'name', 'description', 'products', 'from_unit', 'to_unit', 'ratio',
            'created_on', 'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class ConfigSerializer(PartialUpdateModelSerializer):
    class Meta:
        model = Config
        fields = [
            'notify_by_email', 'notify_on_expiration', 'notify_on_expiration_before',
            'default_expired_action', 'prolong_expired_for', 'notify_on_min_stock',
            #'nofity_on_shopping_plan_generated',
            #'auto_generate_shopping_plan', 
            'allow_replacement_use',
            #'gen_shop_plan_on_min_stock', 'gen_shop_plan_repeatedly', 
            #'gen_shop_plan_period', 
            'base_shop_plan_on_historic_data', 'historic_period', 
            'base_shop_plan_on_cook_plan', 
            'created_on', 'updated_on', 'created_by'
        ]
        read_only_fields = ['created_by', 'created_on', 'updated_on']
