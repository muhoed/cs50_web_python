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
        self.assertEqual(self.testuser.full_name, 'Mr. John Smith')
        self.assertEqual(str(self.testuser), 'Mr. John Smith')
        
    def test_create_email(self):
        additional_email = EmailAddress.objects.create(
                                                user=self.testuser,
                                                email_address='new_email@test.com',
                                                email_type='PT'
                                            )
        self.assertEqual(self.testuser.emailaddress_set.get(pk='1').email_address, 'new_email@test.com')
        self.assertEqual(additional_email.get_email_type_display(), 'Payment')
        self.assertEqual(str(additional_email), 'Email address for payment: new_email@test.com')

    def test_create_address(self):
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
        category = Category.objects.get(id=1)
        
        # testing category __str__ representation
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
        self.assertEqual(
                listing.end_time,
                listing.start_time + datetime.timedelta(days=10)
                )
        self.assertEqual(listing.status, "active")
        self.assertEqual(listing.get_absolute_url(), '/listing/1/')
        self.assertEqual(listing.max_bid, Decimal('1.00'))
        
        
    def test_listing_not_started_status(self):
        self.testlisting.start_time = timezone.now() + datetime.timedelta(days=1)
        self.testlisting.save()
        
        self.assertEqual(self.testlisting.status, "not started yet")
        
    def test_listing_canceled_status(self):
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        
        self.assertEqual(self.testlisting.status, "cancelled")
        
    def test_listing_max_bid(self):
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
        active = Listing.get_active()
        
        self.assertEqual(len(active), 1)
        self.assertTrue(self.testlisting in active)
        
    def test_get_ended_listing(self):
        ended = Listing.get_ended()
        
        self.assertEqual(len(ended), 0)
        
        self.testlisting.cancelled_on = timezone.now()
        self.testlisting.save()
        ended = Listing.get_ended()
        
        self.assertEqual(len(ended), 1)
        self.assertTrue(self.testlisting in ended)
        
    def test_add_to_watchlist(self):
        self.testlisting.followers.add(self.testuser)
        self.testlisting.save()
        
        self.assertEqual(len(self.testuser.watchlist.all()), 1)
        self.assertEqual(self.testuser.watchlist.get(), self.testlisting)
        
    def test_create_bid(self):
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="email1@test.com",
                                password="Pass2%2021")
                                
        # checks ValidationError is raised in pre-save signal callback
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
                                    
        self.assertEqual(str(comment), f"User commenting_user comments on \
auction for testproduct at {comment.time}.")
        
    def test_comment_pending(self):
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
                                    
        self.assertEqual(comment.status, "answered")
        self.assertEqual(len(comment.answer_set.all()), 1)
        
        #test answer __str__
        self.assertEqual(str(answer), f"User test_user answered to \
a comment of commenting_user at {answer.time}.")
        
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
                                    
        
                                    
        self.assertEqual(str(message), f"Message from test_user to recipient regarding test sent at {message.time}.")
