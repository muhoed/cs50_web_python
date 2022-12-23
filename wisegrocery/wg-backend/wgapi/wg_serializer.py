from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import *


class WGTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField()

    class Meta:
        model = WiseGroceryUser
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = WiseGroceryUser.objects.create(
            username=validated_data['username'],
            email = validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

class EquipmentSerializer(serializers.ModelSerializer):
    stockitem_set = serializers.StockItemSetField(many=True)
    class Meta:
        model = Equipment
        fields = [
            'name', 'description', 'type', 'height', 'width', 'depth', 'volume', 
            'rated_size', 'min_tempreture', 'max_tempreture', 'stokitem_set', 
            'created_on', 'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class EquipmentTypeSerializer(serializers.ModelSerializer):
    equipment_set = serializers.EquipmentSetField(many=True)

    class Meta:
        model = EquipmentType
        fields = [
            'name', 'description', 'base_type', 'min_temp', 'max_temp', 'equipment_set',
            'created_on', 'updated_on'
            ]
        read_only_fields = ['equipment_set', 'created_on', 'updated_on']

class ProductSerializer(serializers.ModelSerializer):
    replacement_products = serializers.ReplacementProductsField(many=True)
    recipeproduct_set = serializers.RecipeProductField(many=True)
    conversionrule_set = serializers.ConversionRuleSetField(many=True)
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'manufacturer', 'picture', 
            'minimal_stock_volume', 'minimal_stock_unit', 'alternative_to', 
            'replacement_products', 'recipeproduct_set', 'conversionrule_set',
            'created_on', 'updated_on'
        ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = [
            'product', 'equipment', 'unit', 'volume', 'use_till', 'status', 'created_on',
            'updated_on'
        ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class RecipeSerializer(serializers.ModelSerializer):
    items = serializers.RecipeProductField(many=True)

    class Meta:
        model = Recipe
        fields = [
            'name', 'description', 'items', 'num_persons', 'cookingplan_set',
            'created_on', 'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class RecipeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeProduct
        fields = ['recipe', 'product', 'unit', 'volume', 'created_on', 'updated_on']
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class CookingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingPlan
        fields = ['date', 'meal', 'persons', 'recipe', 'created_on', 'updated_on']
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = [
            'product', 'shop_plan', 'unit', 'volume', 'status', 'created_on', 
            'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class ShoppingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingPlan
        fields = ['date', 'note', 'purchaseitem_set', 'created_on', 'updated_on']
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class ConversionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionRule
        fields = [
            'name', 'description', 'product', 'from_unit', 'to_unit', 'ratio',
            'created_on', 'updated_on'
            ]
        read_only_fields = ['created_on', 'updated_on']
        depth = 1

class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = [
            'notify_by_email', 'notify_on_expiration', 'notify_on_expiration_for',
            'default_expired_action', 'prolong_expired_for', 'notify_on_min_stock',
            'notify_on_min_stock_for', 'nofity_on_shopping_plan_generated',
            'auto_generate_shopping_plan', 'allow_replacement_use',
            'gen_shop_plan_on_min_stock', 'gen_shop_plan_on_historic_data',
            'gen_shop_plan_on_cook_plan', 'created_on', 'updated_on'
        ]
        read_only_fields = ['created_on', 'updated_on']
