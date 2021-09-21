from django import forms
from django.conf import settings as conf_settings
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _

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
		if (not self.forms[1].has_changed() and self.form[1].errors) or (not self.forms[1].has_changed() and self.form[1].errors):
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
	#	if hasattr(self, 'cleaned_data') and \
    #            self.cleaned_data.get('DELETE', False) and \
    #            not self.has_changed():
	#		raise forms.ValidationError('Please fill out the form or remove it.')
			#self._errors = ErrorDict()
			
								
class AddressForm(forms.ModelForm):
	class Meta():
		model = Address
		fields = ('address_type', 'line1', 'line2', 'zip_code', 'city', 'country',)
		
	#def full_clean(self, *args, **kwargs):
	#	super().full_clean(*args, **kwargs)
	#	if hasattr(self, 'cleaned_data') and \
    #            self.cleaned_data.get('DELETE', False) and \
    #            not self.has_changed():
	#		raise forms.ValidationError('Please fill out the form or remove it.')
			#self._errors = ErrorDict()

UserEmailFormset = forms.models.inlineformset_factory(User, EmailAddress,
											form=EmailAddressForm, extra=2,
											formset = RequiredInlineFormSet,
											#min_num=2, validate_min=True, 
											max_num=2, validate_max=True,
											can_delete=True)

UserAddressFormset = forms.models.inlineformset_factory(User, Address,
											form=AddressForm, extra=2,
											formset = RequiredInlineFormSet,
											min_num=1, validate_min=True, 
											max_num=2, validate_max=True, 
											can_delete=True)


class UserPasswordResetForm(PasswordResetForm):
    """
    Adds required attribute to email field and validate whether the provided email
    belongs to some registered user.
    Overrides send_email method to save 'uid' to session in case of FileEmailBackend
    to use it in filename.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    
    def clean_email(self):
        #checks email belongs to a registered user
        data = self.cleaned_data['email']
        if not User.objects.filter(email=data):
            raise ValidationError(_("The provided email does not belong to a valid user account."))
        return data
    
    uid = None
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        #Send a django.core.mail.EmailMultiAlternatives to 'to_email'
        email_backend_type = conf_settings.EMAIL_BACKEND.rsplit(".", 1)[1]
        if email_backend_type == "FileEmailBackend" and context["uid"]:
            self.uid = context["uid"]
        return super().send_mail(subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name)
	
	
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
	
class ListingForm(forms.ModelForm):
	class Meta():
		model = Listing
		fields = ["product", "state", "start_time", "duration", "start_price",
					"payment_policy", "shipment_policy", "return_policy"]
                    
class ProductForm(forms.ModelForm):
	class Meta():
		model = Product
		fields = ["seller", "categories", "name", "description"]
        

class ImageForm(forms.ModelForm):
    class Meta():
        model = Image
        fields = ["image_url"]

ImageFormset = forms.models.inlineformset_factory(Product, Image,
											form=ImageForm, extra=3, 
											max_num=3, validate_max=True)	
