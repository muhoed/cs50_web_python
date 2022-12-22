from django.core import serializers
from rest_framework import serializers as rest_serializers

from .models import Equipment


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
