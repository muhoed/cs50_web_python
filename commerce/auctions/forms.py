from django import forms
from django.conf import settings as conf_settings
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm

from .models import *


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
			raise forms.ValidationError('Please complete required information.')


class RegisterForm(UserCreationForm):
	email = forms.EmailField(label="Email address")
	
	class Meta(UserCreationForm.Meta):
		model = User
		fields = UserCreationForm.Meta.fields + \
					("email",)
					  
					
class UserFullNameForm(forms.ModelForm):
	class Meta():
		model = User
		fields = ("title", "first_name", "last_name",)
					
class EmailAddressForm(forms.ModelForm):
	class Meta():
		model = EmailAddress
		fields = ("email_address", "email_type",) 
		
	#def full_clean(self, *args, **kwargs):
	#	super().full_clean(*args, **kwargs)
	#	if hasattr(self, 'cleaned_data') and self.cleaned_data.get('DELETE', False):
	#		self._errors = ErrorDict()
			
								
class AddressForm(forms.ModelForm):
	class Meta():
		model = Address
		fields = ('address_type', 'line1', 'line2', 'zip_code', 'city', 'country',)
		
	#def full_clean(self, *args, **kwargs):
	#	super().full_clean(*args, **kwargs)
	#	if hasattr(self, 'cleaned_data') and self.cleaned_data.get('DELETE', False):
	#		self._errors = ErrorDict()

UserEmailFormset = forms.models.inlineformset_factory(User, EmailAddress,
											form=EmailAddressForm, min_num=0,
											formset = RequiredInlineFormSet,
											max_num=2, validate_max=True,
											can_delete=True)

UserAddressFormset = forms.models.inlineformset_factory(User, Address,
											form=AddressForm,
											min_num=1, validate_min=True, 
											max_num=2, validate_max=True, 
											can_delete=True)


class UserPasswordResetForm(PasswordResetForm):
    """
    Override send_email method to save 'uid' to session in case of FileEmailBackend
    to use it in filename.
    """
    uid = None
    
    def send_mail(self, *args, **kwargs):
        #Send a django.core.mail.EmailMultiAlternatives to 'to_email'
        email_backend_type = type(conf_settings.EMAIL_BACKEND)
        if email_backend_type.__name__ == "FileEmailBackend":
            self.uid = context["uid"]
        return super().send_mail(*args, **kwargs)
	
	
class SearchForm(forms.Form):
	watched = forms.CharField(label="Search", max_length=100)
	
class PlaceBidForm(forms.ModelForm):
	class Meta():
		model = Bid
		fields = ["value"]
	
class CommentForm(forms.ModelForm):
	class Meta():
		model = Comment
		fields = ["content"]
	
class AnswerForm(forms.ModelForm):
	class Meta():
		model = Answer
		fields = ["content"]
	
class CreateListingForm(forms.ModelForm):
	class Meta():
		model = Listing
		fields = ["product", "start_time", "duration", "start_price",
					"state", "payment_policy", "shipment_policy", "return_policy"]
	
