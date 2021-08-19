from .models import Category
from .forms import SearchForm


def categories_processor(request):
	"""
	Context processor to render list of categories at every project page.
	"""
	return {'categories_list':
		Category.objects.all(),}

def search_form_processor(request):
	"""
	Context processor to add search form to every page.
	"""
	sform = SearchForm()
	return {'sform': sform,}
