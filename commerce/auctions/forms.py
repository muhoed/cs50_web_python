from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Profile, Bid, Comment, Answer, Listing


class RequiredInlineFormSet(forms.BaseInlineFormSet):
	"""
	Creates inline formset that is required.
	"""		
	def _construct_form(self, i, **kwargs):
		form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
		form.empty_permitted = False
		return form
		
	def clean(self):
		super().clean()
		if any(self.errors):
			return
		if not self.forms[0].has_changed():
			raise forms.ValidationError('Please fill in your profile information.')

class RegisterForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User
		fields = UserCreationForm.Meta.fields + \
					('email',)
					
class ProfileForm(forms.ModelForm):
    class Meta():
        model = Profile
        exclude = ('user',)

UserProfileFormset = forms.models.inlineformset_factory(User, Profile,
											form=ProfileForm,
											formset = RequiredInlineFormSet, 
											extra=1, can_delete=False,
											min_num=1, validate_min=True)

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
	
