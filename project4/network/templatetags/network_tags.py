from django import template
from django.core.serializers import serialize

register = template.Library()

@register.filter
def object_jsonify(obj):
    return serialize("json", [obj,])

@register.filter
def queryset_count(obj):
    return obj.count()