from django.test import TestCase
from django.urls import reverse
from django.test import Client

from auctions.models import *


class TestViews(TestCase):
	
    def setUp(self):
        # Create test user to use in testing.
        self.testuser = User.objects.create_user("test_user", "", 'Pass&2021')
        #self.testuser.save()
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
                            
    def test_index_view_no_listing(self):
        #Issue a GET request
        response = self.client.get(reverse('auctions:index'))
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        #Check if base template is used
        self.assertTemplateUsed('/auctions/layout.html')
        #Check if view specific template is used
        self.assertTemplateUsed('/auctions/index.html')
        #Check one category is in context
        self.assertEqual(len(response.context['categories_list']), 1)
        #Check there are no listings and respective message is displayed
        self.assertEqual(len(response.context['active_listings_list']), 0)
        self.assertContains(response, "There are no active listings at the moment.")
        
    def test_index_view_two_listings(self):
        listing = Listing.objects.create(product=self.product)
        response = self.client.get(reverse('auctions:index'))
        
        self.assertEqual(len(response.context['active_listings_list']), 1)
        self.assertContains(response, "Testproduct")
        
    def test_user_login_bad_credentials(self):
        response = self.client.post(reverse('auctions:login'),
                                    {'username': 'somename', 'password': 'somepassword'},
                                    follow=True)
        
        self.assertContains(response, 'Invalid username and/or password.')
