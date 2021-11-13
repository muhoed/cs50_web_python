from django.contrib import admin

from .models import *


# Register your models here.
@admin.register(User, EmailAddress, Address, Category, Product, Image, Listing, Bid, Comment, Answer, Message)
class CommerceAdmin(admin.ModelAdmin):
	pass
