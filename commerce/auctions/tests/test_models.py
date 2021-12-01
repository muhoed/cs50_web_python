import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from auctions.models import *

    					
class TestModels(TestCase):
    """
    Testing models logic including pre- and post-save signal handlers 
    except built-in Django functionality.
    """
	
    def setUp(self):
        # Create test user to use in testing
        self.testuser = User.objects.create_user(
                                        username="test_user",
                                        email="test_email@test.com",
                                        password='Pass&2021',
                                        title="MR",
                                        first_name="John",
                                        last_name="Smith"
                                        )
        # Create test user delivery address to use in testing
        self.testuser.address_set.add(Address.objects.create(
                                        user=self.testuser,
                                        line1="street 1",
                                        zip_code="99999",
                                        city="city"
                                        ))
        
        # Create test category
        self.category = Category.objects.create(
                            name="testcategory",
                            description="category for testing purposes")
        # Create test product
        self.product = self.category.products.create(
                            name="testproduct",
                            description="Product for testing purposes",
                            seller = self.testuser
                            )
        self.testlisting = Listing.objects.create(product=self.product)
        
    def test_user_atributes(self):
        # testing User class properties and methods are functional
        self.assertEqual(self.testuser.full_name, 'Mr. John Smith')
        self.assertEqual(str(self.testuser), 'Mr. John Smith')
        
    def test_create_email(self):
        # testing Email object methods and properties
        additional_email = EmailAddress.objects.create(
                                                user=self.testuser,
                                                email_address='new_email@test.com',
                                                email_type='PT'
                                            )
                                            
        self.assertEqual(additional_email.get_email_type_display(), 'Payment')
        self.assertEqual(str(additional_email), 'Email address for payment: new_email@test.com')

    def test_create_address(self):
        # testing Address object methods and properties
        address = Address.objects.create(user=self.testuser,
                                            line1='street 1',
                                            zip_code='00000',
                                            city='testcity',
                                            country='SK',
                                            address_type='BL' 
                                            )
                                            
        self.assertEqual(address.get_country_display(), 'Slovakia')
        self.assertEqual(address.get_address_type_display(), 'Billing address')
        self.assertEqual(str(address), 'Billing address: street 1, 00000 testcity, Slovakia')
        
    def test_new_category(self):
        # testing category __str__ representation
        category = Category.objects.get(id=1)
        
        self.assertEqual(str(category), 'testcategory')
        
    def test_new_product(self):
        product = Product.objects.get(id=1)
        
        # testing product __str__ representation
        self.assertEqual(str(product), 'Product title: testproduct, product description: Product for testing purposes')
        
        # testing a message to  product seller was created by product post-save handler
        message = Message.objects.filter(subject="Product testproduct was added").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
    def test_sold_num_product(self):
        # testing Product object sold_num properties
        testbidder = User.objects.create(
                                username="testbidder",
                                email="",
                                password="Pass2%2021")
        testbidder.address_set.add(Address.objects.create(
                                        user=testbidder,
                                        line1="street 1",
                                        zip_code="99999",
                                        city="city"
                                        ))
        bid1 = Bid.objects.create(bidder=testbidder, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        testlisting2 = Listing.objects.create(product=self.product)
        bid2 = Bid.objects.create(bidder=testbidder, 
                                listing=testlisting2, 
                                value=Decimal('2.00'))
        testlisting2.cancelled_on = timezone.now()
        testlisting2.save()
        
        self.assertEqual(self.product.sold_num, 2)
	
    def test_new_listing(self):
        listing = Listing.objects.get(id=1)
        
        # testing pre-save signal handler that sets value of end_time field
        self.assertEqual(
                listing.end_time,
                listing.start_time + datetime.timedelta(days=10)
                )
                
        # testing a message to listing product's seller was created by post-save signal handler
        message = Message.objects.filter(subject="Listing for testproduct was created").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
        # testing initial values of listing properties
        self.assertEqual(listing.status, "active")
        self.assertEqual(listing.get_absolute_url(), '/listing/1/')
        self.assertEqual(listing.max_bid, Decimal('1.00'))
        
        
    def test_listing_not_started_status(self):
        # testing listing not started yet status
        self.testlisting.start_time = timezone.now() + datetime.timedelta(days=1)
        self.testlisting.save()
        
        self.assertEqual(self.testlisting.status, "not started yet")
        
    def test_listing_canceled_status(self):
        # testing listing cancelled status
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        
        self.assertEqual(self.testlisting.status, "cancelled")
        
    def test_listing_max_bid(self):
        # testing listing max_bid property
        testbidder = User.objects.create(
                                username="testbidder",
                                email="",
                                password="Pass2%2021")
        bid1 = Bid.objects.create(bidder=testbidder, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        bid2 = Bid.objects.create(bidder=testbidder, 
                                listing=self.testlisting, 
                                value=Decimal('3.15'))
        
        self.assertEqual(self.testlisting.max_bid, bid2.value)
        
    def test_listing_winner(self):
        # testing listing winner property
        self.testlisting.duration = datetime.timedelta(days=0)
        self.testlisting.save()
        
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="email1@test.com",
                                password="Pass2%2021")
        bidder2 = User.objects.create(
                                username="bidder2",
                                email="email2@test.com",
                                password="Pass3%2021")
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        bid2 = Bid.objects.create(bidder=bidder2, 
                                listing=self.testlisting, 
                                value=Decimal('3.15'))
        bid3 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('4.00'))
        
        self.assertEqual(self.testlisting.winner, bidder1)
        
    def test_get_active_listing(self):
        # testing Listing get_active() classmethod
        active = Listing.get_active()
        
        self.assertEqual(len(active), 1)
        self.assertTrue(self.testlisting in active)
        
    def test_get_ended_listing(self):
        # testing Listing get_ended() classmethod
        ended = Listing.get_ended()
        
        self.assertEqual(len(ended), 0)
        
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        ended = Listing.get_ended()
        
        self.assertEqual(len(ended), 1)
        self.assertTrue(self.testlisting in ended)
        
    def test_message_no_bidder_cancelled_listing(self):
        # testing post-save signal handler behavior in case of listing 
        # cancelled before any bid was placed
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        
        # testing a message to listing product's seller was sent by post-save signal handler
        message = Message.objects.filter(subject="Auction$' listing for testproduct was cancelled").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
    def test_message_winner_cancelled_listing(self):
        # testing post-save signal handler behavior in case of listing 
        # cancelled after two bids were placed
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="email1@test.com",
                                password="Pass2%2021")
        bidder2 = User.objects.create(
                                username="bidder2",
                                email="email2@test.com",
                                password="Pass3%2021")
        bidder2.address_set.add(Address.objects.create(
                                        user=bidder2,
                                        line1="street 1",
                                        zip_code="99999",
                                        city="city"
                                        ))
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        bid2 = Bid.objects.create(bidder=bidder2, 
                                listing=self.testlisting, 
                                value=Decimal('3.15'))
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        
        # testing a message to listing product's seller was sent by post-save signal handler
        message = Message.objects.filter(content__contains="You just cancelled the listing for testproduct").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
        # testing a message to listing's winner was sent by post-save signal handler
        message = Message.objects.filter(content__contains="Congratulation! You are the winner in the Auction$ listing \
        for testproduct").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, bidder2)
        
    def test_message_paid_marked_listing(self):
        # testing post-save signal handler behavior in case of listing 
        # was paid before shipment (default case)
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="email1@test.com",
                                password="Pass2%2021")
        bidder1.address_set.add(Address.objects.create(
                                        user=bidder1,
                                        line1="street 1",
                                        zip_code="99999",
                                        city="city"
                                        ))
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        
        self.testlisting.paid = True
        self.testlisting.save()
        
        # testing a message to listing product's seller was sent by post-save signal handler
        message = Message.objects.filter(content__contains="Buyer marked the listing for testproduct").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
    def test_message_shipped_before_payment_listing(self):
        # testing post-save signal handler behavior in case of listing 
        # was shipment before payment made by buyer
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="email1@test.com",
                                password="Pass2%2021")
        bidder1.address_set.add(Address.objects.create(
                                        user=bidder1,
                                        line1="street 1",
                                        zip_code="99999",
                                        city="city"
                                        ))
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        
        # seller marked listing's product as shipped
        self.testlisting.shipment_status = 1
        self.testlisting.save()
        
        # testing a message to listing product's seller was sent by post-save signal handler
        message = Message.objects.filter(content__contains="We noted however that the product was not marked as 'Paid'").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, bidder1)
        
    def test_message_shipped_delivered_listing(self):
        # testing post-save signal handler behavior in case of listing 
        # was shipped after payment and then marked as delivered (default case)
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="email1@test.com",
                                password="Pass2%2021")
        bidder1.address_set.add(Address.objects.create(
                                        user=bidder1,
                                        line1="street 1",
                                        zip_code="99999",
                                        city="city"
                                        ))
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        
        #buyer marked listing as paid
        self.testlisting.paid = True
        self.testlisting.save()
        
        # seller marked listing as shipped
        self.testlisting.shipment_status = 1
        self.testlisting.save()
        
        # buyer marked listing as delivered
        self.testlisting.shipment_status = 2
        self.testlisting.save()
        
        # testing correct message was sent by post-save signal handler
        message = Message.objects.filter(content__contains="We noted however that the product was not marked as 'Paid'").first()
        self.assertFalse(message)
        
        message = Message.objects.filter(content__contains="shipped it to the delivery address stored in your profile").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, bidder1)
        
        message = Message.objects.filter(subject="The listing for testproduct was marked as 'Delivered'").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
    def test_message_modified_listing(self):
        # testing post-save signal handler behavior in case of listing 
        # modification
        self.testlisting.duration = datetime.timedelta(days=5)
        self.testlisting.save()
        
        # testing a message to listing product's seller was sent by post-save signal handler
        message = Message.objects.filter(subject="Listing for testproduct was modified").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
    def test_add_to_watchlist(self):
        # testing add to user watchlist logic 
        self.testlisting.followers.add(self.testuser)
        self.testlisting.save()
        
        self.assertEqual(len(self.testuser.watchlist.all()), 1)
        self.assertEqual(self.testuser.watchlist.get(), self.testlisting)
        
    def test_create_bid(self):
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="email1@test.com",
                                password="Pass2%2021")
                                
        # checks ValidationError is raised by pre-save signal handler
        # of Bid class in case of bid's value less or equal to the existing
        # highest bid on the listing
        message = f"Your bid is less or equal to the current \
highest bid. Please increase a bid value and \
try again. Current highest bid is %s" % self.testlisting.max_bid
        
        with self.assertRaisesMessage(
                            ValidationError,
                            message):
                                Bid.objects.create(bidder=bidder1, 
                                                listing=self.testlisting, 
                                                value=Decimal('1.00'))
        
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('2.00'))
        
        # assert Bid class __str__ method works as expected
        self.assertEqual(str(bid1), f"User bidder1 bidded 2.00 at {bid1.time}.")
        
        # testing a messages to bidder and listing product's seller was created by post-save signal handler
        message1 = Message.objects.filter(subject="You've just placed a bid on Auction$' listing for testproduct").first()
        message2 = Message.objects.filter(subject="User bidder1 placed a bid in your listing for testproduct").first()
        self.assertTrue(message1)
        self.assertTrue(message2)
        self.assertEqual(message1.recipient, bidder1)
        self.assertEqual(message2.recipient, self.testuser)
        
    def test_comment(self):
        user = User.objects.create(
                                    username="commenting_user", 
                                    email="", 
                                    password="Pass&2021"
                                    )
        comment = Comment.objects.create(
                                    author = user,
                                    listing = self.testlisting,
                                    content = "test comment"
                                    )
        # testing comment __str__ representation                            
        self.assertEqual(str(comment), f"User commenting_user comments on \
auction for testproduct at {comment.time}.")

        # testing a message to listing product's seller was created by post-save signal handler
        message = Message.objects.filter(subject__contains="Comment was left in your listing on").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, self.testuser)
        
    def test_comment_pending(self):
        # testing comment status
        user = User.objects.create(
                                    username="commenting_user", 
                                    email="", 
                                    password="Pass&2021"
                                    )
        comment = Comment.objects.create(
                                    author = user,
                                    listing = self.testlisting,
                                    content = "test comment"
                                    )
                                    
        self.assertEqual(comment.status, "pending")
        
    def test_comment_answered_answer(self):
        user = User.objects.create(
                                    username="commenting_user", 
                                    email="", 
                                    password="Pass&2021"
                                    )
        comment = Comment.objects.create(
                                    author = user,
                                    listing = self.testlisting,
                                    content = "test comment"
                                    )
        answer = Answer.objects.create(
                                    respondent = self.testuser,
                                    comment = comment,
                                    content = "test answer"
                                    )
        # testing comment status changed                            
        self.assertEqual(comment.status, "answered")
        # testing answer linked to comment
        self.assertEqual(len(comment.answer_set.all()), 1)
        
        #test answer __str__
        self.assertEqual(str(answer), f"User test_user answered to \
a comment of commenting_user at {answer.time}.")

        # testing a message to commenter was created by post-save signal handler
        # after the comment was answered
        message = Message.objects.filter(subject__contains="Your comment was answered by test_user").first()
        self.assertTrue(message)
        self.assertEqual(message.sender.username, "system")
        self.assertEqual(message.recipient, user)
        
    def test_message(self):
        user = User.objects.create(
                                    username="recipient", 
                                    email="recipient@test.com", 
                                    password="Pass&2021"
                                    )
        message = Message.objects.create(
                                    sender = self.testuser,
                                    recipient = user,
                                    listing = self.testlisting,
                                    subject = "test",
                                    content = "test message content"
                                    )
                                    
        # testing message __str__ representation
        self.assertEqual(str(message), f"Message from test_user to recipient regarding test sent at {message.time}.")
