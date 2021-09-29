from django import template

register = template.Library()

class SetFlagNode(template.Node):
		
	def render(self, context):
		if not hasattr(context, "flag"):
			context["flag"] = 0
		else:
			context["flag"] = 1
		return ''

@register.tag(name="setflag")		
def set_flag(parser, token):
	return SetFlagNode()
