from django.test import TestCase
from django.urls import reverse
from django.test import Client

from auctions.models import *


class TestViews(TestCase):
	
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
                            
    def test_index_view_no_listing_user_not_logged_in(self):
        #Issue a GET request
        response = self.client.get(reverse('auctions:index'))
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        #Check one category is in context
        self.assertEqual(len(response.context['categories_list']), 1)
        #Check there are no listings and respective message is displayed
        self.assertEqual(len(response.context['active_listings']), 0)
        self.assertContains(response.content, 'There are no active listings \
                                                                at the moment.')
        
