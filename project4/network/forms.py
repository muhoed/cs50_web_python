from django import forms

class AvatarUploadForm(forms.Form):
    # upload form for user avatar image
    id = forms.IntegerField()
    avatar = forms.ImageField()

