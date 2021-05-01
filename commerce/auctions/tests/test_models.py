import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from auctions.models import *

    					
class TestModels(TestCase):
	
    def setUp(self):
        # Create test user to use in testing.
        self.testuser = User.objects.create_user("test_user", "", 'Pass&2021')
        self.testuser.save()
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
	
    def test_listing_end_time(self):
        testlisting = Listing.objects.create(product=self.product)
        
        self.assertEqual(testlisting.end_time-testlisting.start_time, 
                            datetime.timedelta(days=10))
                            
    def test_listing_default_status(self):
        testlisting = Listing.objects.create(product=self.product)
        
        self.assertEqual(testlisting.status, "active")
        
    def test_listing_not_started_status(self):
        testlisting = Listing.objects.create(
                        product=self.product,
                        start_time = timezone.now() + datetime.timedelta(days=1)
                        )
        
        self.assertEqual(testlisting.status, "not started yet")
        
    def test_listing_canceled_status(self):
        testlisting = Listing.objects.create(
                                product=self.product,
                                cancelled=True
                                )
        
        self.assertEqual(testlisting.status, "cancelled")
        
    def test_listing_no_bid_max(self):
        testlisting = Listing.objects.create(product=self.product)
        
        self.assertEqual(testlisting.max_bid, 0)
        
    def test_listing_max_bid(self):
        testlisting = Listing.objects.create(product=self.product)
        testbidder = User.objects.create(
                                username="testbidder",
                                email="",
                                password="Pass2%2021")
        bid1 = Bid.objects.create(bidder=testbidder, 
                                listing=testlisting, 
                                value=Decimal('1.00'))
        bid2 = Bid.objects.create(bidder=testbidder, 
                                listing=testlisting, 
                                value=Decimal('3.15'))
        
        self.assertEqual(testlisting.max_bid, bid2.value)
        
    def test_listing_winner(self):
        testlisting = Listing.objects.create(
                                        product=self.product,
                                        duration = datetime.timedelta(days=0)
                                        )
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="",
                                password="Pass2%2021")
        bidder2 = User.objects.create(
                                username="bidder2",
                                email="",
                                password="Pass3%2021")
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=testlisting, 
                                value=Decimal('1.00'))
        bid2 = Bid.objects.create(bidder=bidder2, 
                                listing=testlisting, 
                                value=Decimal('3.15'))
        bid3 = Bid.objects.create(bidder=bidder1, 
                                listing=testlisting, 
                                value=Decimal('4.00'))
        
        self.assertEqual(testlisting.winner, bidder1)
        
    def test_comment_pending(self):
        testlisting = Listing.objects.create(product=self.product)
        user = User.objects.create(
                                    username="commenting_user", 
                                    email="", 
                                    password="Pass&2021"
                                    )
        comment = Comment.objects.create(
                                    author = user,
                                    listing = testlisting,
                                    content = "test comment"
                                    )
                                    
        self.assertEqual(comment.status, "pending")
        
    def test_comment_answered(self):
        testlisting = Listing.objects.create(product=self.product)
        user = User.objects.create(
                                    username="commenting_user", 
                                    email="", 
                                    password="Pass&2021"
                                    )
        comment = Comment.objects.create(
                                    author = user,
                                    listing = testlisting,
                                    content = "test comment"
                                    )
        answer = Answer.objects.create(
                                    respondent = self.testuser,
                                    comment = comment,
                                    content = "test answer"
                                    )
                                    
        self.assertEqual(comment.status, "answered")
        
