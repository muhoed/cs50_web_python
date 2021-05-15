from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Contact, Bid, Comment, Answer, Listing


class RegisterForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User
		fields = UserCreationForm.Meta.fields + \
					('email',)
					
class ContactForm(forms.ModelForm):
    class Meta():
        model = Contact

class SearchForm(forms.Form):
	watched = forms.CharField(label="Search", max_length=100)
	
class PlaceBidForm(forms.ModelForm):
	class Meta():
		model = Bid
		fields = ['value']
	
class CommentForm(forms.ModelForm):
	class Meta():
		model = Comment
		fields = ['content']
	
class AnswerForm(forms.ModelForm):
	class Meta():
		model = Answer
		fields = ['content']
	
class CreateListingForm(forms.ModelForm):
	class Meta():
		model = Listing
		fields = ['product', 'start_time', 'duration', 'start_price',
					'state', 'payment_policy', 'shipment_policy', 'return_policy']
	
