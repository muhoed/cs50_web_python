from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register([User, Post, Comment, Reaction, ViewedPost])
