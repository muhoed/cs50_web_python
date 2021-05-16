from django.contrib import admin

from .models import User, Contact, Category, Product, Image, Listing, Bid, Comment, Answer


# Register your models here.
@admin.register(User, Contact, Category, Product, Image, Listing, Bid, Comment, Answer)
class CommerceAdmin(admin.ModelAdmin):
	pass
