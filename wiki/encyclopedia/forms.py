from django import forms


class createForm(forms.Form):
	ftype = forms.CharField(initial='new', widget=forms.HiddenInput())
	title = forms.CharField(label="Article title:", max_length=100,
							widget=forms.TextInput(attrs={'class':'form-control'}))
	content = forms.CharField(label="Content:", 
								widget=forms.Textarea(attrs={'class':'form-control',
															 'rows':'5'}))
