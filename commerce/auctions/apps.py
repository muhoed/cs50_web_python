from django.apps import AppConfig
from django.db.models.signals import post_save, post_migrate


class AuctionsConfig(AppConfig):
    name = 'auctions'
    
    #def ready(self):
        #from .models import Product, Listing, Bid, Comment, Answer
