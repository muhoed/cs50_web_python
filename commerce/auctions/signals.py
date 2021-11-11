from django.db.models.signals import post_save, pre_save, post_migrate
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.translation import gettext, gettext_lazy as _

from .models import Product, Listing, Bid, Comment, Answer, Message, User

def get_sys_user():
    try:
        sys_user = User.objects.get(username="system")
    except:
        sys_user = User.objects.create(username="system", email="noreplay@auctions.demo", password="system")
    

def get_url_detais():
    current_site = get_current_site(request)
    domain = current_site.domain
    return "http://" + domain
        

@receiver(post_save, sender=Product)
def product_handler(sender, instance, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.seller
    subject = _("Product %s was added") % instance.name
    content = _("The product '%(prod)' was added.\nGo to the <a href='%(url)'>\
    product page</a> to see or modify its details and create listing to sell it \
    on Auction$.\nThis message is autogenerated. Do not reply.") %\
                {'prod': instance.name,
                'url': get_url_details() + "/account/" + recipient.pk + "/product/" + instance.pk + "/"}
    Message.objects.create(sender=sysuser.pk, recipient=recipient.pk, 
										subject=subject, content=content
										)
    
@receiver(post_save, sender=Listing)
def listing_handler(sender, instance, created, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.product.seller
    if created:
        subject = _("Listing for %s was created") % instance.product.name
        content = _("Listing was created. Details: %(listing).\nClick <a href=\
        '%(url)'>here</a> to manage listing.\nThis message is autogenerated. \
        Do not reply.") % {
                'listing': instance, 
                'url': get_url_details() + "/account/" + recipient.pk + "/listing/" + instance.pk + "/"
                }
    elif instance.cancelled_on and instance.winner and instance.shipment_status == 0 and not instance.paid:
        recipient1 = instance.winner
        subject = _("Listing for %s was cancelled by the seller") % instance.product.name
        content = _("You just cancelled the listing for %(product).\
        \nThe user %(user) placed the highest bid up now and is the listing winner.\
        \nYou can contact the winner through the 'Contact buyer' button on <a href=\
        '%(url)'>the listing page</a> or directly by email %(email).\nPlease make \
        sure you ship the product to the winner at her/his delivery address:%(address).\
        \nThis message is autogenerated. Do not reply.") %\
                    {
                    'product': instance.product.name, 
                    'user': recipient1.username, 
                    'url': get_url_detais() + "/account/" + recipient.pk + "/listing/" + instance.pk + "/", 
                    'email': recipient1.emailaddress_set.filter(email_type='CT').values('email_address') or recipient1.email, 
                    'address': recipient1.address_set.get(address_type='DL')
                    }
        content1 = _("Congratulation! You are the winner in the Auction$ listing \
        for %(prod).\nThe listing was finished by the seller on %(time) before the \
        planned end time.\nYou can contact the seller through the 'Contact seller' \
        button on <a href='%(url)'>the listing page</a> or directly by email \
        %(email).\nPayment for the product shall be sent to %(email1). Please make \
        sure you mark the listing as 'Paid' after the payment is done. The product \
        will be shipped to your delivery address at:\n%(address). Please mark it as \
        'Delivered' upon receipt if it meets the listing description and conditions.\
        \nThis message is autogenerated. Do not reply." ) %\
                    {
                    'prod': instance.product.name, 
                    'time': instance.cancelled_on, 
                    'url': get_url_detais() + "/listing/" + instance.pk + "/", 
                    'email': recipient.emailaddress_set.filter(email_type='CT').values('email_address') or recipient.email, 
                    'email1': recipient.emailaddress_set.filter(email_type='PT').values('email_address') or recipient.email, 
                    'address': recipient1.address_set.get(address_type='DL')
                    }
        Message.objects.create(sender=sysuser.pk, recipient=recipient1.pk, 
                                            subject=subject, content=content1
                                            )
    elif instance.paid and instance.shipment_status == 0:
        subject = _("The listing for %s was marked as 'Paid'") % instance.product.name
        content = _("Buyer marked the listing for %(prod) as 'Paid'. The product \
        shall be sent to the buyer's delivery address at %(address). Please make \
        sure you mark the listing as 'Shipped' after the shipment is done.\nThis \
        message is autogenerated. Do not reply.") %\
                    {
                        'prod': instance.product.name,
                        'address': instance.winner.address_set.get(address_type='DL')
                    }
    elif not instance.paid and instance.shipment_status == 1:
        recipient = instance.winner
        subject = _("Product %s was shipped to you") % instance.product.name
        content = _("The seller of the product %(prod) you recently bought on \
        Auction$ shipped it to the delivery address stored in your profile:\
        \n%(address).\nWe noted however that the product was not marked as 'Paid' \
        by you. Payment for the product shall be sent to the seller's email \
        address %(email1) through [SOME PAYMENT SYSTEM HERE]. Please make sure you \
        mark the listing as 'Paid' after the payment is done.\nPlease ignore the \
        note above if you have already paid for the product and just mark it as \
        'Paid'.\nPlease mark the product as 'Delivered' upon receipt if it meets \
        the listing description and conditions. You can do it as well as contact \
        the seller through the respective buttons on <a href='%(url)'>the listing \
        </a>. You can also contact the seller directly by email %(email).\nThis \
        message is autogenerated. Do not reply.") %\
                    {
                    'prod': instance.product.name, 
                    'url': get_url_detais() + "/listing/" + instance.pk + "/", 
                    'email': instance.product.seller.emailaddress_set.filter(email_type='CT').values('email_address') or instance.product.seller.email,  
                    'email1': instance.product.seller.emailaddress_set.filter(email_type='PT').values('email_address') or instance.product.seller.email, 
                    'address': recipient.address_set.get(address_type='DL')
                    }
    elif instance.shipment_status == 1:
        
        recipient = instance.winner
        subject = _("Product %s was shipped to you") % instance.product.name
        content = _("The seller of the product %(prod) you recently bought on \
        Auction$ shipped it to the delivery address stored in your profile:\
        \n%(address).\nPlease mark the product as 'Delivered' upon receipt if it \
        meets the listing description and conditions. You can do it as well as \
        contact the seller through the respective buttons on <a href='%(url)'>the \
        listing page</a>. You can also contact the seller directly by email \
        %(email).\nThis message is autogenerated. Do not reply.") %\
                    {
                    'prod': instance.product.name, 
                    'url': get_url_detais() + "/listing/" + instance.pk + "/", 
                    'email': instance.product.seller.emailaddress_set.filter(email_type='CT').values('email_address') or instance.product.seller.email, 
                    'address': recipient.address_set.get(address_type='DL')
                    }
    elif instance.shipment_status == 2:
        subject = _("The listing for %s was marked as 'Delivered'") % instance.product.name
        content = _("The buyer marked the listing for %(prod) as 'Delivered'.\nThis \
        message is autogenerated. Do not reply.") %\
                    {
                        'prod': instance.product.name
                    }
    else:
        subject = _("Listing for %s was modified") % instance.product.name
        content = _("You just modified the listing for %(prod). See the listing \
        details at <a href='%(url)'>the listing page</a>.\nThis message is \
        autogenerated. Do not reply.") %\
                    {
                        'prod': instance.product.name,
                        'url': get_url_detais() + "/account/" + recipient.pk + "/listing/" + instance.pk + "/"
                    }
    Message.objects.create(sender=sysuser.pk, recipient=recipient.pk, 
                                        subject=subject, content=content
                                        )

@receiver(post_save, sender=Comment)
def comment_handler(sender, instance, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.listing.product.seller
    subject = _("Comment was left in your listing on %s") % instance.time
    content = _("User %(user) left a comment in your listing for %(prod) \
    on %(time).\nComment's content:\n%(content)\nGo to <a href='%(url)'>here</a> \
    to manage listing.\nThis message is autogenerated. Do not reply.") %\
                                        {
                                        'user': instance.author.name,
                                        'prod': instance.listing.product.name,
                                        'time': instance.time,
                                        'content': instance.content,
                                        'url': get_url_detais() + "/account/" + recipient.pk + "/listing/" + instance.listing.pk + "/"
                                        }
    Message.objects.create(sender=sysuser.pk, recipient=recipient.pk, 
										subject=subject, content=content
										)
										
@receiver(post_save, sender=Answer)
def answer_handler(sender, instance, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.comment.author
    subject = _("Your comment was answered by %(user) on %(time)") %\
                            {
                            'user': instance.respondent.username,
                            'time': instance.time
                            }
    content = _("The seller of %(prod) answered your comment left on the respective \
    listing.\nText of your initial comment:\n%(comment)\nAnswered by %(respondent)\
     on %(time).\nAnswer's content:\n%(answer)\nGo to <a href='%(url)'>here</a> to \
     see listing details.\nThis message is autogenerated. Do not reply.") %\
                            {
                            'prod': instance.comment.listing.product.name,
                            'comment': instance.comment.content,
                            'respondent': instance.respondent.username,
                            'time': instance.time,
                            'answer': instance.content,
                            'url': get_url_detais() + "/listing/" + instance.comment.listing.pk + "/'"
                            }
    Message.objects.create(sender=sysuser.pk, recipient=recipient.pk, 
										subject=subject, content=content
										)
										
@receiver(pre_save, sender=Bid)
def pre_bid_handler(sender, instance, **kwargs):
    if float(instance.value) <= float(instance.listing.max_bid):
        messages.failure = (request, f"Your bid is less or equal to the current highest bid. Please increase a bid value and try again. Current highest bid is %s" % str(instance.listing.max))
        return HttpResponse("Failed")

@receiver(post_save, sender=Bid)
def bid_handler(sender, instance, **kwargs):
    sysuser = User.objects.get(username="system") #get_sys_user()
    print(sysuser+'\n')
    recipient1 = instance.bidder
    print(recipient1+'\n')
    recipient2 = instance.listing.product.seller
    subject1 = _("You've just placed a bid on Auction$' listing for  %s") %\
                                                        instance.listing.product.name
    subject2 = _("User %(user) placed a bid in your listing for %(prod)") %\
                                                {
                                                'user': instance.bidder.username,
                                                'prod': instance.listing.product.name
                                                }
    content1 = _("You have placed a new bid on the following listing:\n%(listing)\
    \nBid amount: %(amount)€\nBid time: %(time)\nGo to <a href='%(url)'>listing \
    page</a> to see details.\nThis message is autogenerated. Do not reply.") %\
                {
                    'listing': instance.listing,
                    'amount': instance.value,
                    'time': instance.time,
                    'url': get_url_detais() + "/listing/" + instance.listing.pk + "/"
                    }
    content2 = _("A bid was placed in your listing for %(prod).\nBidder: %(bidder)\
    \nBid amount: %(amount)€\nBid time: %(time)\nGo to <a href='%(url)'>listing \
    page</a> to see details.\nThis message is autogenerated. Do not reply.") %\
                {
                    'prod': instance.listing.product.name,
                    'bidder': instance.bidder.username,
                    'amount': instance.value,
                    'time': instance.time,
                    'url': get_url_detais() + "/account/" + recipient.pk + "/listing/" + instance.listing.pk + "/"
                    }
    message1 = Message.objects.create(sender=sysuser.pk, recipient=recipient1.pk, 
													subject=subject1, content=content1
													)
    message2 = Message.objects.create(sender=sysuser.pk, recipient=recipient2.pk, 
													subject=subject2, content=content2
													)
