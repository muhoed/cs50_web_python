import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate

from auctions.models import *

    					
class TestModels(TestCase):
	
    def setUp(self):
        # Create test user to use in testing.
        self.testuser = User.objects.create_user("test_user", "", 'Pass&2021')
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
        
    def test_create_profile(self):
        profile = Contact.objects.create(user = self.testuser,
                                            title = 'MR',
                                            first_name = 'Test',
                                            last_name = 'Testoff',
                                            line1 = 'street 1',
                                            zip_code = '00000',
                                            city = 'testcity',
                                            country = 'SK'
                                            )
        self.assertEqual(profile.get_title_display(), 'Mr.')
        self.assertEqual(profile.get_country_display(), 'Slovakia')
        self.assertEqual(self.testuser.contact_details.full_name, 'Test Testoff')
        self.assertEqual(str(self.testuser.contact_details), 'Mr. Test Testoff')
    
    def test_bad_credentials(self):
        self.assertFalse(authenticate(username='test_user', password='somepass'))
        
    def test_good_credentials(self):
        self.assertTrue(authenticate(username='test_user', password='Pass&2021'))
	
    def test_new_listing(self):
        listing = Listing.objects.get(id=1)
        self.assertEqual(listing.end_time-listing.start_time, 
                                                        datetime.timedelta(days=10))
        self.assertEqual(listing.status, "active")
        self.assertEqual(listing.get_absolute_url, '/listing/1/')
        self.assertEqual(listing.max_bid, 0)
        
        
    def test_listing_not_started_status(self):
        self.testlisting.start_time = timezone.now() + datetime.timedelta(days=1)
        self.testlisting.save()
        
        self.assertEqual(self.testlisting.status, "not started yet")
        
    def test_listing_canceled_status(self):
        self.testlisting.cancelled = True
        self.testlisting.save()
        
        self.assertEqual(self.testlisting.status, "cancelled")
        
    def test_listing_max_bid(self):
        testbidder = User.objects.create(
                                username="testbidder",
                                email="",
                                password="Pass2%2021")
        bid1 = Bid.objects.create(bidder=testbidder, 
                                listing=self.testlisting, 
                                value=Decimal('1.00'))
        bid2 = Bid.objects.create(bidder=testbidder, 
                                listing=self.testlisting, 
                                value=Decimal('3.15'))
        
        self.assertEqual(self.testlisting.max_bid, bid2.value)
        
    def test_listing_winner(self):
        self.testlisting.duration = datetime.timedelta(days=0)
        self.testlisting.save()
        
        bidder1 = User.objects.create(
                                username="bidder1",
                                email="",
                                password="Pass2%2021")
        bidder2 = User.objects.create(
                                username="bidder2",
                                email="",
                                password="Pass3%2021")
        bid1 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('1.00'))
        bid2 = Bid.objects.create(bidder=bidder2, 
                                listing=self.testlisting, 
                                value=Decimal('3.15'))
        bid3 = Bid.objects.create(bidder=bidder1, 
                                listing=self.testlisting, 
                                value=Decimal('4.00'))
        
        self.assertEqual(self.testlisting.winner, bidder1)
        
    def test_add_to_watchlist(self):
        self.testlisting.followers.add(self.testuser)
        self.testlisting.save()
        
        self.assertEqual(len(self.testuser.watchlist.all()), 1)
        self.assertEqual(self.testuser.watchlist.get(), self.testlisting)
        
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
        
    def test_comment_answered(self):
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
        
