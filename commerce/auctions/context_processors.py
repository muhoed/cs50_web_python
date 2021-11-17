from .models import Category, Message
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
	
def unread_messages_number_processor(request):
    """
    Context processor to add number of unread messages to page context.
    """
    if request.user.is_authenticated:
        return {'num_unread': Message.objects.filter(read=False, recipient=request.user).count(),}
    return {'num_unread': 0}
