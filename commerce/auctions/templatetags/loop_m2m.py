from django import template

register = template.Library()

@register.simple_tag
def loop_m2m(entity, relation):
	if not hasattr(entity, relation):
		raise AttributeError
	return [item for item in getattr(entity, relation)]
