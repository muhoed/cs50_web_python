from django.core import serializers
from rest_framework import serializers as rest_serializers


class EquipmentSetField(rest_serializers.RelatedField):
    def to_representation(self, value):
        return serializers.serialize(
            'json', [ value, ], fileds=[
                'name', 'volume', 'rated_size', 'min_tempreture', 'max_tempreture'
                ]
            )

class ReplacementProductsField(rest_serializers.RelatedField):
    def to_representation(self, value):
        return serializers.serialize(
            'json', [ value, ], fields=['name', 'category']
        )

class StockItemSetField(rest_serializers.RelatedField):
    def to_representation(self, value):
        return serializers.serialize(
            'json', [ value, ], fields=['product', 'unit', 'volume', 'use_till', 'status']
        )

class RecipeProductField(rest_serializers.RelatedField):
    def to_representation(self, value):
        return serializers.serialize(
            'json', [ value, ], fields=['recipe', 'product', 'unit', 'volume']
        )

class ConversionRuleSetField(rest_serializers.RelatedField):
    def to_representation(self, value):
        return serializers.serialize(
            'json', [ value, ], fields=['name', 'from_unit', 'to_unit', 'ratio']
        )

class ConversionRuleProductSetField(rest_serializers.RelatedField):
    def to_representation(self, value):
        return serializers.serialize(
            'json', [ value, ], fields=['id', 'name', 'category']
        )
