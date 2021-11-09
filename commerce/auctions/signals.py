from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from auctions.models import Product, Listing, Bid, Comment, Answer, Message


@receiver(post_save, sender=Product)
def my_handler(sender, **kwargs):
    recipient = sender.instance.seller
    subject = _("Product") + sender.instance.name + _("added")
    content = _("The product'") + sender.instance.name + _("' was added.")
    return system_message()