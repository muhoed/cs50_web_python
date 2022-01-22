from django.apps import AppConfig


class AuctionsConfig(AppConfig):
    name = 'auctions'
    
    def ready(self):
        from .signals import product_handler, listing_handler, comment_handler, answer_handler, bid_handler #, pre_bid_handler
