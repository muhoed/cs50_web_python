from .models import Category


def categories_processor(request):
	"""
	Context processor to render list of categories at every project page.
	"""
	return {'categories_list':
		Category.objects.all(),}
