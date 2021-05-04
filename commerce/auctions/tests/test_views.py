from django.test import TestCase
from django.urls import reverse
from django.test import Client

from auctions.models import *


class TestViews(TestCase):
	
    @classmethod
    def setUpTestData(cls):
        """
        Prepare a set of data to be used in all tests without modification.
        """
        # Create test users to use in testing.
        self.testuser1 = User.objects.create_user("test_user1", "", 'Pass1')
        self.testuser2 = User.objects.create_user("test_user2", "", 'Pass2')
        self.testuser3 = User.objects.create_user("test_user3", "", 'Pass3')
        # Create test categories
        self.category1 = Category.objects.create(
                            name="testcategory1",
                            description="category1 for testing purposes")
        self.category2 = Category.objects.create(
                            name="testcategory2",
                            description="category2 for testing purposes")
        # Create test products
        self.product1 = self.category1.products.create(
                            name="testproduct1",
                            description="Product1 for testing purposes",
                            seller = self.testuser1
                            )
        self.product2 = self.category2.products.create(
                            name="testproduct2",
                            description="Product2 for testing purposes",
                            seller = self.testuser2
                            )
                            
    def test_index_view_url(self):
        """
        Test checks url is reachable.
        """
        #Issue a GET request
        response = self.client.get('/')
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_url_name_no_listing(self):
        """
        Test checks: 
        - url naming is working, 
        - correct templates are used,
        - search form is displayed, 
        - there are two categories and no active listings.
        """
        #Issue a GET request
        response = self.client.get(reverse('auctions:index'))
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        #Check if base template is used
        self.assertTemplateUsed('/auctions/layout.html')
        #Check if view specific template is used
        self.assertTemplateUsed('/auctions/index.html')
        #Check one category is in context
        self.assertEqual(len(response.context['categories_list']), 2)
        #Check search form is displayed
        self.assertContains(response, "<form id='searchForm'")
        #Check there are no listings and respective message is displayed
        self.assertEqual(len(response.context['active_listings_list']), 0)
        self.assertContains(response, "There are no active listings at the moment.")
        
    def test_index_view_two_listings(self):
        """
        Test checks: 
        - all existing active listings are transmitted to template 
        and displayed,
        - 'add to watchlist' form is displayd for all listings
        - 'place bid' button is displayed for all listings
        """
        #Create two listings and issue GET request
        listing1 = Listing.objects.create(product=self.product1)
        listing2 = Listing.objects.create(product=self.product2)
        response = self.client.get(reverse('auctions:index'))
        
        #Check two listings are in context
        self.assertEqual(len(response.context['active_listings_list']), 2)
        #Check listing1 and related 'add to watchlist' form
        #and 'place bid' button are displayed
        self.assertContains(response, listing1.get_absolute_url)
        self.assertContains(response, "Testproduct1")
        self.assertContains(response, "<form id='listing_'"+listing1.id)
        self.assertContains(response, "<a href=''")
        
        self.assertContains(response, listing2.get_absolute_url)
        self.assertContains(response, "Testproduct2")
        
    def test_user_login_bad_credentials(self):
        response = self.client.post(reverse('auctions:login'),
                                    {'username': 'somename', 'password': 'somepassword'},
                                    follow=True)
        
        self.assertContains(response, 'Invalid username and/or password.')
