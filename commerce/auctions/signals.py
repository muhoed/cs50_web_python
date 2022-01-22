from django.db.models.signals import post_save, pre_save, post_migrate
from django.dispatch import receiver
from django.utils.translation import gettext, gettext_lazy as _
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from .models import Product, Listing, Bid, Comment, Answer, Message, User, get_sys_user
from .tasks import listing_ended_handler
        

@receiver(post_save, sender=Product)
def product_handler(sender, instance, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.seller
    subject = _("Product %s was added") % instance.name
    content = _("The product '%(prod)s' was added.<br>Go to the <a href='%(url)s'>\
    product page</a> to see or modify its details and create listing to sell it \
    on Auction$.<br>This message is autogenerated. Do not reply.") %\
                {'prod': instance.name,
                'url': instance.get_absolute_url()}
    Message.objects.create(sender=sysuser, recipient=recipient, 
										subject=subject, content=content
										)

@receiver(pre_save, sender=Listing)
def pre_listing_handler(sender, instance, **kwargs):
    instance.end_time = instance.start_time + instance.duration
    
@receiver(post_save, sender=Listing)
def listing_handler(sender, instance, created, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.product.seller
    if created:
        subject = _("Listing for %s was created") % instance.product.name
        content = _("Listing was created. Details: %(listing)s.<br>Click <a href=\
        '%(url)s'>here</a> to manage listing.<br>This message is autogenerated. \
        Do not reply.") % {
                'listing': instance, 
                'url': instance.get_absolute_url()
                }
        
        #initiate task to send message(-es) once listing ended
        try:
            listing_ended_handler.apply_async(({'pk': instance.pk},), eta=instance.end_time)
        except Exception as e:
            print(e)
        
    elif instance.cancelled_on and not instance.winner:
        subject = _("Auction$' listing for %s was cancelled") %\
                    instance.product.name
        content = _("You've just cancelled a listing on Auction$. \
        <br>Details: %(listing)s.<br>Click <a href='%(url)s'>here</a> to relist product.\
        <br>This message is autogenerated. Do not reply.") % {
                'listing': instance, 
                'url': instance.get_absolute_url()
                }
    elif instance.cancelled_on and instance.winner and instance.shipment_status == 0 and not instance.paid:
        recipient1 = instance.winner
        subject = _("Listing for %s was cancelled by the seller") % instance.product.name
        content = _("You just cancelled the listing for %(product)s.\
        <br>The user %(user)s placed the highest bid and is the listing winner.\
        <br>You can contact the winner through the 'Contact buyer' button on <a href=\
        '%(url)s'>the listing page</a> or directly by email %(email)s.<br>Please make \
        sure you ship the product to the winner at her/his delivery address upon payment.\
        <br>%(address)s.<br>This message is autogenerated. Do not reply.") %\
                    {
                    'product': instance.product.name, 
                    'user': recipient1.username, 
                    'url': instance.get_absolute_url(), 
                    'email': recipient1.emailaddress_set.filter(email_type='CT').values('email_address') or recipient1.email, 
                    'address': recipient1.address_set.get(address_type='DL')
                    }
        content1 = _("Congratulation! You are the winner in the Auction$ listing \
        for %(prod)s.<br>The listing was finished by the seller on %(time)s before the \
        planned end time.<br>You can contact the seller through the 'Contact seller' \
        button on <a href='%(url)s'>the listing page</a> or directly by email \
        %(email)s.<br>Payment for the product shall be sent to %(email1)s. Please make \
        sure you mark the listing as 'Paid' after the payment is done. The product \
        will be shipped to your delivery address at:<br>%(address)s.<br>Please mark it as \
        'Delivered' upon receipt if it meets the listing description and conditions.\
        <br>This message is autogenerated. Do not reply." ) %\
                    {
                    'prod': instance.product.name, 
                    'time': instance.cancelled_on, 
                    'url': instance.get_absolute_url(), 
                    'email': recipient.emailaddress_set.filter(email_type='CT').values('email_address') or recipient.email, 
                    'email1': recipient.emailaddress_set.filter(email_type='PT').values('email_address') or recipient.email, 
                    'address': recipient1.address_set.get(address_type='DL')
                    }
        Message.objects.create(sender=sysuser, recipient=recipient1, 
                                            subject=subject, content=content1
                                            )
    elif instance.paid and instance.shipment_status == 0:
        subject = _("The listing for %s was marked as 'Paid'") % instance.product.name
        content = _("Buyer marked the listing for %(prod)s as 'Paid'. The product \
        shall be sent to the buyer's delivery address at:<br>%(address)s. Please make \
        sure you mark the listing as 'Shipped' after the shipment is done.<br>This \
        message is autogenerated. Do not reply.") %\
                    {
                        'prod': instance.product.name,
                        'address': instance.winner.address_set.get(address_type='DL')
                    }
    elif not instance.paid and instance.shipment_status == 1:
        recipient = instance.winner
        subject = _("Product %s was shipped to you") % instance.product.name
        content = _("The seller of the product %(prod)s you recently bought on \
        Auction$ shipped it to the delivery address stored in your profile:\
        <br>%(address)s.<br>We noted however that the product was not marked as 'Paid' \
        by you. Payment for the product shall be sent to the seller's email \
        address %(email1)s through [SOME PAYMENT SYSTEM HERE]. Please make sure you \
        mark the listing as 'Paid' after the payment is done.<br>Please ignore the \
        note above if you have already paid for the product and just mark it as \
        'Paid'.<br>Please mark the product as 'Delivered' upon receipt if it meets \
        the listing description and conditions. You can do it as well as contact \
        the seller through the respective buttons on <a href='%(url)s'>the listing \
        page</a>. You can also contact the seller directly by email %(email)s.<br>This \
        message is autogenerated. Do not reply.") %\
                    {
                    'prod': instance.product.name, 
                    'url': instance.get_absolute_url(), 
                    'email': instance.product.seller.emailaddress_set.filter(email_type='CT').values('email_address') or instance.product.seller.email,  
                    'email1': instance.product.seller.emailaddress_set.filter(email_type='PT').values('email_address') or instance.product.seller.email, 
                    'address': recipient.address_set.get(address_type='DL')
                    }
    elif instance.shipment_status == 1:
        
        recipient = instance.winner
        subject = _("Product %s was shipped to you") % instance.product.name
        content = _("The seller of the product %(prod)s you recently bought on \
        Auction$ shipped it to the delivery address stored in your profile:\
        <br>%(address)s.<br>Please mark the product as 'Delivered' upon receipt if it \
        meets the listing description and conditions. You can do it as well as \
        contact the seller through the respective buttons on <a href='%(url)s'>the \
        listing page</a>. You can also contact the seller directly by email \
        %(email)s.<br>This message is autogenerated. Do not reply.") %\
                    {
                    'prod': instance.product.name, 
                    'url': instance.get_absolute_url(), 
                    'email': instance.product.seller.emailaddress_set.filter(email_type='CT').values('email_address') or instance.product.seller.email, 
                    'address': recipient.address_set.get(address_type='DL')
                    }
    elif instance.shipment_status == 2:
        subject = _("The listing for %s was marked as 'Delivered'") % instance.product.name
        content = _("The buyer marked the listing for %(prod)s as 'Delivered'.<br>This \
        message is autogenerated. Do not reply.") %\
                    {
                        'prod': instance.product.name
                    }
    else:
        subject = _("Listing for %s was modified") % instance.product.name
        content = _("You just modified the listing for %(prod)s. See the listing \
        details at <a href='%(url)s'>the listing page</a>.<br>This message is \
        autogenerated. Do not reply.") %\
                    {
                        'prod': instance.product.name,
                        'url': instance.get_absolute_url()
                    }
    Message.objects.create(sender=sysuser, recipient=recipient, 
                                        subject=subject, content=content
                                        )

@receiver(post_save, sender=Comment)
def comment_handler(sender, instance, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.listing.product.seller
    subject = _("Comment was left in your listing on %s") % instance.time
    content = _("User %(user)s left a comment in your listing for %(prod)s \
    on %(time)s.<br>Comment's content:<br>%(content)s<br>Go to <a href='%(url)s'>here</a> \
    to manage listing.<br>This message is autogenerated. Do not reply.") %\
                                        {
                                        'user': instance.author.username,
                                        'prod': instance.listing.product.name,
                                        'time': instance.time,
                                        'content': instance.content,
                                        'url': instance.listing.get_absolute_url()
                                        }
    Message.objects.create(sender=sysuser, recipient=recipient, 
										subject=subject, content=content
										)
										
@receiver(post_save, sender=Answer)
def answer_handler(sender, instance, **kwargs):
    sysuser = get_sys_user()
    recipient = instance.comment.author
    subject = _("Your comment was answered by %(user)s on %(time)s") %\
                            {
                            'user': instance.respondent.username,
                            'time': instance.time
                            }
    content = _("The seller of %(prod)s answered your comment left on the respective \
    listing.<br>Text of your initial comment:<br>%(comment)s<br>Answered by %(respondent)s\
     on %(time)s.<br>Answer's content:<br>%(answer)s<br>Go to <a href='%(url)s'>here</a> to \
     see listing details.<br>This message is autogenerated. Do not reply.") %\
                            {
                            'prod': instance.comment.listing.product.name,
                            'comment': instance.comment.content,
                            'respondent': instance.respondent.username,
                            'time': instance.time,
                            'answer': instance.content,
                            'url': instance.comment.listing.get_absolute_url()
                            }
    Message.objects.create(sender=sysuser, recipient=recipient, 
										subject=subject, content=content
										)
										
@receiver(pre_save, sender=Bid)
def pre_bid_handler(sender, instance, **kwargs):
    if float(instance.value) <= float(instance.listing.max_bid):
		
        raise ValidationError({"value": f"Your bid is less or equal to the current \
highest bid. Please increase a bid value and \
try again. Current highest bid is %s" % str(instance.listing.max_bid)})

@receiver(post_save, sender=Bid)
def bid_handler(sender, instance, **kwargs):
    sysuser = get_sys_user()
    recipient1 = instance.bidder
    recipient2 = instance.listing.product.seller
    subject1 = _("You've just placed a bid on Auction$' listing for %s") %\
                                                        instance.listing.product.name
    subject2 = _("User %s placed a bid in your listing for %s") %\
                                                (
                                                instance.bidder.username,
                                                instance.listing.product.name
                                                )
    content1 = _("You have placed a new bid on the following listing: %(listing)s. \
    <br>Bid amount: %(amount)s€<br>Bid time: %(time)s.<br>Go to <a href='%(url)s'>\
    listing page</a> to see details.<br>This message is autogenerated. Do not reply.") % \
                {
                    'listing': instance.listing,
                    'amount': str(instance.value),
                    'time': instance.time,
                    'url': instance.listing.get_absolute_url()
                    }
    content2 = _("A bid was placed in your listing for %(prod)s.<br>Bidder: %(bidder)s\
    <br>Bid amount: %(amount)s€<br>Bid time: %(time)s<br>Go to <a href='%(url)s'>listing \
    page</a> to see details.<br>This message is autogenerated. Do not reply.") %\
                {
                    'prod': instance.listing.product.name,
                    'bidder': instance.bidder.username,
                    'amount': str(instance.value),
                    'time': instance.time,
                    'url': instance.listing.get_absolute_url()
                    }
    message1 = Message.objects.create(sender=sysuser, recipient=recipient1, 
													subject=subject1, content=content1
													)
    message2 = Message.objects.create(sender=sysuser, recipient=recipient2, 
													subject=subject2, content=content2
													)
