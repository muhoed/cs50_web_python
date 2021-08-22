import random
import re

from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

#import subprocess
#import shlex
import psutil
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC

from auctions.models import *


class TestViews(TestCase):
    """
    Test mixin class to create data to all child test classes.
    """
	
    @classmethod
    def setUpTestData(cls):
        """
        Prepare a set of data to be used in all tests without modification.
        """
        # Create test users to use in testing.
        User.objects.create_user("test_user1", "", 'Pass1',
                                    title="MR", first_name="User1",
                                    last_name="User_1")
        User.objects.create_user("test_user2", "", 'Pass2',
                                    title="MS", first_name="User2",
                                    last_name="User_2")
        User.objects.create_user("test_user3", "", 'Pass3')
        # Create additional email for test_user1
        user1 = User.objects.get(username='test_user1')
        EmailAddress.objects.create(user=user1, 
										email_address="user1@test.com",
										email_type="CT")
        # Create address for test_user1
        Address.objects.create(user=user1,
                                line1='street 1', zip_code='00000',
                                city='testcity', country='SK',
                                address_type="DL")
        # Mark user1 profile as completed
        user1.profile_completed = True
        user1.save()
        # Create test categories
        Category.objects.create(
                            name="testcategory1",
                            description="category1 for testing purposes"
                            )
        Category.objects.create(
                            name="testcategory2",
                            description="category2 for testing purposes"
                            )
        #Create test products
        Product.objects.create(
                            name="testproduct1",
                            description="Product1 for testing purposes",
                            seller=get_object_or_404(User, id=1)
                            )
        Product.objects.create(
                            name="testproduct2",
                            description= "Product2 for testing purposes",
                            seller=get_object_or_404(User, id=2)
                            )
        category1 = Category.objects.get(id=1)
        category2 = Category.objects.get(id=2)
        category1.products.add(Product.objects.get(id=1))
        category1.save()
        category2.products.add(Product.objects.get(id=2))
        category2.save()                    
                            
class TestIndexView(TestViews):
    """
    Set of tests to check home page view.
    """
                            
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
        - correct template is used,
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
        self.assertContains(response, '<input type="text"')
        
        #Check there are no listings and respective message is displayed
        self.assertEqual(len(response.context['listing_list']), 0)
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
        product1 = get_object_or_404(Product, id=1)
        product2 = get_object_or_404(Product, id=2)
        listing1 = Listing.objects.create(product=product1)
        listing2 = Listing.objects.create(product=product2)
        response = self.client.get(reverse('auctions:index'))
        
        #Check two listings are in context
        self.assertEqual(len(response.context['listing_list']), 2)
        
        #Check listing1 and related 'add to watchlist' form,
        #'place bid' button and link are displayed
        self.assertContains(response, '<a href="'+listing1.get_absolute_url)
        self.assertContains(response, "Testproduct1")
        self.assertContains(response, '<form id="listing_'+str(listing1.id))
        
        #Check listing2 and related 'add to watchlist' form,
        #'place bid' button and link are displayed
        self.assertContains(response, '<a href="'+listing2.get_absolute_url)
        self.assertContains(response, "Testproduct2")
        self.assertContains(response, '<form id="listing_'+str(listing2.id))
        
    def test_index_view_active_listings(self):
        """
        Test checks: 
        - only active listings are displayed.
        """
        #Create two listings, cancel one of them and issue GET request
        product1 = get_object_or_404(Product, id=1)
        product2 = get_object_or_404(Product, id=2)
        listing1 = Listing.objects.create(product=product1)
        listing2 = Listing.objects.create(product=product2)
        listing2.cancelled = True
        listing2.save()
        response = self.client.get(reverse('auctions:index'))
        
        #Check listing1 is displayed
        self.assertContains(response, "Testproduct1")
        
        #Check listing2 is not displayed
        self.assertNotContains(response, "Testproduct2")
        
    def test_index_view_pagination_10(self):
        """
        Test checks: 
        - max 10 listings are displayed on a page
        - there are respective pagination navigation
        - only remaining listings are displayed on the second screens.
        """
        #Create 13 listings and issue GET request
        for i in range(13):
            random_product = Product.objects.get(id=random.choice([1,2]))
            Listing.objects.create(product=random_product)
        response = self.client.get(reverse('auctions:index'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['page_obj'].number, 1)
        self.assertTrue(response.context['page_obj'].has_next)
        #self.assertFalse(response.context['page_obj'].has_previous)
        self.assertEqual(len(response.context['listing_list']), 10)

        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('auctions:index')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertTrue(response.context['page_obj'].has_previous)
        self.assertFalse(response.context['page_obj'].has_next)
        self.assertEqual(len(response.context['listing_list']), 3)
        
        
class TestLoginView(TestViews):
    """
    Set of tests to check login page view and logout function.
    """
    
    def test_login_view_url(self):
        """
        Test checks url is reachable.
        """
        #Issue a GET request
        response = self.client.get('/login')
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
    def test_login_view_url_name(self):
        """
        Test checks url naming works and correct template
        is used.
        """
        #Issue a GET request
        response = self.client.get(reverse('auctions:login'))

        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)

        #Check correct template is used
        self.assertTemplateUsed('/auctions/auth/login.html')
    
    def test_user_login_bad_credentials(self):
        """
        Test checks error message appears while using bad credentials
        and user in session is still AnonymousUser.
        """
        #Try to log with non-existing username and password in
        response = self.client.post(reverse('auctions:login'),
                                    {'username': 'somename', 
                                    'password': 'somepassword'})
        
        #Check error message is displayed
        self.assertContains(response, 'Please enter a correct username and password.')
        
        #Check user in session is anonymous
        self.assertFalse(response.context['user'].is_authenticated)
        
    def test_user_login_good_credentials(self):
        """
        Test checks user with correct credentials is logged in and
        redirect to home page works.
        """
        #Try to log with correct username and password in
        response = self.client.post(reverse('auctions:login'),
                                    {'username': 'test_user1', 
                                    'password': 'Pass1'}, follow=True)
        
        #Check user in session is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        #Check if user data are correct
        u = get_object_or_404(User, id=1)
        self.assertEqual(str(response.context['user']), str(u))
        
        #Check user was redirected to profile page
        self.assertRedirects(response, reverse(
                                'auctions:profile', 
                                kwargs={
                                    'pk':u.pk
                                }))
        
    def test_user_logout(self):
        """
        Checks if user after logout is AnonymousUser instance.
        """
        #Try to log with correct username and password in
        response = self.client.post(reverse('auctions:login'),
                                    {'username': 'test_user1', 
                                    'password': 'Pass1'}, follow=True)
        
        #Check user in session is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        
        #Log user out
        response = self.client.get(reverse('auctions:logout'), follow=True)
        
        #Check user in session is anonymous
        self.assertFalse(response.context['user'].is_authenticated)
        
class TestRegisterView(TestViews):
    """
    Tests user registration process.
    """
    
    def test_register_view_url(self):
        """
        Tests url is reachable, url naming works and correct template is used.
        """
        #Issue a GET request
        response = self.client.get('/register')
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
    def test_register_view_url_name(self):
        """
        Test checks url naming works and correct template
        is used.
        """
        #Issue a GET request
        response = self.client.get(reverse('auctions:register'))

        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)

        #Check correct template is used
        self.assertTemplateUsed('/auctions/auth/register.html')
        
    def test_register_form_displayed(self):
        """
        Test that register form is displayed.
        """
        #Issue a GET request
        response = self.client.get(reverse('auctions:register'))

        #Check register form is in content 
        self.assertContains(response, '<form action="/register" method="post">')
        
    def test_register_user_empty_data(self):
        """
        Test that register view returns error if no data are provided.
        """
        #Issue a POST request with empty data
        response = self.client.post(reverse('auctions:register'),
                                    {'username':'', 'email':'', 'password':'',
                                        'confirmation':''})

        #Check the page is loaded 
        self.assertEqual(response.status_code, 200)
        #Check errors are displayed by the form
        self.assertFormError(response, 'form', 
                                'username', 'This field is required.')
        self.assertFormError(response, 'form', 
                                'password1', 'This field is required.')
        self.assertFormError(response, 'form', 
                                'password2', 'This field is required.')
        
    def test_register_user_bad_email(self):
        """
        Test that register view returns error if provided email is not valid.
        """
        #Issue a POST request with empty data
        response = self.client.post(reverse('auctions:register'),
                                                    {'username':'testname',
                                                    'email':'email.com',
                                                    'password':'testpass',
                                                    'confirmation':'testpass'})

        #Check errors are displayed by the form
        self.assertFormError(response, 'form', 
                                'email', 'Enter a valid email address.')
        
    def test_register_user_weak_password(self):
        """
        Test that register view returns error if provided password is too weak.
        """
        #Issue a POST request with weak password
        response = self.client.post(reverse('auctions:register'),
                                                    {'username':'testname',
                                                    'email':'test@test.com',
                                                    'password1':'111',
                                                    'password2':'111'})
        
        #Check errors are displayed by the form
        self.assertFormError(response, 'form',
                                'password2', ['This password is too short. It must contain at least 8 characters.',
                                'This password is too common.',
                                'This password is entirely numeric.'])
    
    def test_bad_password_confirmation(self):
        """
        Test that register view returns error if password and password confirmation 
        are not equal.
        """
        #Issue a POST request with incorrect data
        response = self.client.post(reverse('auctions:register'),
                                                    {'username':'testname',
                                                    'email':'test@test.com',
                                                    'password1':'111',
                                                    'password2':'11'})
        self.assertFormError(response, 'form',
                                'password2', 'The two password fields didn’t match.')                                            
        
        
    def test_register_user_duplicate_name(self):
        """
        Test that register view returns error if provided name is already in use.
        """
        #Issue a POST request with name that already exists
        response = self.client.post(reverse('auctions:register'),
                                                    {'username':'test_user1',
                                                    'email':'test@test.com',
                                                    'password1':'Pass&2021',
                                                    'password2':'Pass&2021'})

        #Check errors are displayed by the form
        self.assertFormError(
                    response, 'form', 'username', 
                    'A user with that username already exists.'
                    )
        
    def test_register_user_right_data(self):
        """
        Test that user is redirected to account activation page when 
        form is filled correctly.
        Test user becomes active and is redirected to activation confirmation
        page once activation link was used.
        """
        #Issue a POST request with correct and complete data
        response = self.client.post(reverse('auctions:register'),
                                                        {'username':'test_user4',
                                                        'email':'test@test.com',
                                                        'password1':'Pass&2021',
                                                        'password2':'Pass&2021'},
                                                        follow=True)
        u = User.objects.get(username='test_user4')
        #Check user is not active yet
        self.assertFalse(u.is_active)
        #Check user was redirected to account activation page
        self.assertRedirects(response, reverse('auctions:registration_confirm'), 
                                status_code=302, target_status_code=200,
                                fetch_redirect_response=True)
        

class TestRegistrationConfirmView(TestViews):
    """
    Tests user account activation process.
    """
    token_generator = default_token_generator
    
    def setUp(self):
        """
        Prepare data common for all tests in this class.
        """
        
        self.u = User.objects.get(username='test_user3')
        self.domain = 'testserver'
        self.uid_test = urlsafe_base64_encode(force_bytes(self.u.pk))
        self.token_test = self.token_generator.make_token(self.u)
        #Set session variable 'newuser'
        session = self.client.session
        session["newuser"] = self.u.pk
        session.save()
        
    def test_registration_confirm_view_url(self):
        """
        Tests url is reachable, url naming works and correct template is used.
        """
        #Issue a GET request
        response = self.client.get('/registration_confirm')
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
    def test_registration_confirm_view_url_name(self):
        """
        Test checks url naming works and correct template
        is used.
        """
        #Issue a GET request
        response = self.client.get(reverse('auctions:registration_confirm'))

        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)

        #Check correct template is used
        self.assertTemplateUsed('/auctions/auth/registration_confirm.html')
                
    def test_registration_confirm_message(self):
        """
        Test that registration confirmation screen is correct.
        """
        
        #Issue a get request to confirm view
        response = self.client.get(reverse('auctions:registration_confirm'))
        
        #Check is message about successfull registration is displayed
        self.assertContains(response, '<div id="activation_message">')
        #Check response contains URL parts of activation link and they are correct
        self.assertEqual(response.context["uid"], self.uid_test)
        self.assertEqual(response.context["token"], self.token_test)
        self.assertContains(response, 
            "http://" + self.domain + "/registration_complete/" + self.uid_test + "/" + self.token_test)


class TestRegistrationCompleteView(TestViews):
    """
    Tests user account activation process.
    """
    token_generator = default_token_generator
    
    def setUp(self):
        """
        Prepare data common for all tests in this class.
        """
        self.u = User.objects.get(username='test_user3')
        self.u.is_active = False
        self.domain = 'testserver'
        self.uid_test = urlsafe_base64_encode(force_bytes(self.u.pk))
        self.token_test = self.token_generator.make_token(self.u)
                    					
    def test_wrong_complete_registration_data(self):
        """
        Test user account is not activated and an error message is displayed
        if data sent with request are invalid.
        """
        u1 = User.objects.get(username="test_user2")
        uid1 = urlsafe_base64_encode(force_bytes(u1.pk))
        token1 = self.token_generator.make_token(u1)
		
        #Send request with wrong uid
        response = self.client.get(reverse('auctions:registration_complete',
                                                        args=[uid1, self.token_test,]),
                                                        follow=True)
        #Check link is not validated
        self.assertFalse(response.context["validlink"])
        #Check error message is displayed
        self.assertContains(response, "Activation link you used seems to be wrong or not valid any more.")
        #Check current user is active
        self.assertFalse(self.u.is_active)
        
        #Send request with wrong token
        response = self.client.get(reverse('auctions:registration_complete',
                                                        args=[self.uid_test, token1,]),
                                                        follow=True)
        #Check link is not validated
        self.assertFalse(response.context["validlink"])
        #Check error message is displayed
        self.assertContains(response, "Activation link you used seems to be wrong or not valid any more.")
        #Check current user is active
        self.assertFalse(self.u.is_active)
					
						
    def test_complete_registration_right_data(self):
        """
        Test that user is redirected to account activation page when 
        form is filled correctly.
        Test user becomes active and is redirected to activation confirmation
        page once activation link was used.
        """
        
        #Check link redirects user to activation complete view and
        #user is activated then
        response = self.client.get(reverse('auctions:registration_complete',
														args=[self.uid_test, self.token_test,]),
														follow=True)
		
		#Check user was redirected to activation confirmation page
        self.assertRedirects(response, reverse('auctions:registration_complete',
                                args=[self.uid_test, 'activate-user',]), 
                                status_code=302, target_status_code=200,
                                fetch_redirect_response=True)
        #Check if correct template is used
        self.assertTemplateUsed('auctions/auth/registration_complete.html')
        #Check link is validated successfully
        self.assertTrue(response.context["validlink"])
        #Check successfull activation message is displayed
        self.assertContains(response, "Activation of your account was successfull.")
        #Check if the user account was activated
        self.u.refresh_from_db()
        self.assertTrue(self.u.is_active)

            
class TestProfileView(TestViews):
    """
    Tests user profile view.
    """
    def setUp(self):
        """
        Prepare data common for all tests in this class.
        """
        
        self.user = User.objects.get(username="test_user2")
        if self.user is not None:
            self.client.force_login(self.user)
        
    def test_profile_view_url(self):
        """
        Tests url is reachable, url naming works and correct template is used.
        """
        #Issue a GET request
        response = self.client.get('/profile/' + str(self.user.pk) + '/')
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
    def test_profile_view_url_name(self):
        """
        Test checks url naming works and correct template
        is used.
        """
        #Issue a GET request
        response = self.client.get(reverse(
                                        'auctions:profile', args=[self.user.pk,]
                                        ))

        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)

        #Check correct template is used
        self.assertTemplateUsed('/auctions/account/profile.html')
        
    def test_non_completed_profile(self):
        """
        Tests whether respective message is displayed to a new user
        who did not filled in her/his profile information yet.  
        """
            
        #request profile page
        response = self.client.get(reverse('auctions:profile', args=[self.user.pk,]))
        
        #check if user profile is incomplete
        self.assertFalse(self.user.profile_completed)
        #check if a message about incomplete profile is displayed
        self.assertContains(response, "Your profile information is incomplete!")
        #check if a link to create profile page is displayed
        self.assertContains(response, '<a href="' + reverse(
                                                        'auctions:create_profile', 
                                                        args=[self.user.pk,]
                                                        ))
		

class TestCreateProfileView(TestViews):
    """
    Tests profile creation view for a new user.
    """
    
    def setUp(self):
        """
        Prepare data common for all tests in this class.
        """
        self.user = User.objects.get(username='test_user3')
        if self.user is not None:
            self.client.force_login(self.user)
        #set fields values as on actual web-page
        self.data = {
            'title': '',
            'first_name': '',
            'last_name': '',
            'emailaddress_set-TOTAL_FORMS': '2',
            'emailaddress_set-INITIAL_FORMS': '0',
            'emailaddress_set-0-email_address': '',
            'emailaddress_set-0-email_type': 'CT',
            'emailaddress_set-0-DELETE': True,
            'emailaddress_set-1-email_address': '',
            'emailaddress_set-1-email_type': 'PT',
            'emailaddress_set-1-DELETE': True,
            'addres_set-TOTAL_FORMS': '2',
            'address_set-INITIAL_FORMS': '0',
            'address_set-0-address_type': 'DL',
            'address_set-0-line1': '',
            'address_set-0-line2': '', #not required field
            'address_set-0-zip_code': '',
            'address_set-0-city': '',
            'address_set-0-country': 'SK',
            'address_set-0-DELETE': False,
            'address_set-1-address_type': 'BL',
            'address_set-1-line1': '',
            'address_set-1-line2': '', #not required field
            'address_set-1-zip_code': '',
            'address_set-1-city': '',
            'address_set-1-country': 'SK',
            'address_set-1-DELETE': True
        }
        
    def set_data(
            self, full_name=False, 
            first_email=False, second_email=False,
            first_address=False, second_address=False
                ):
        if full_name:
            #fill out full name form
            self.data['title'] = 'MR'
            self.data['first_name'] = 'User'
            self.data['last_name'] = 'useroff'
        if fisrt_email:
            #fill out first email address form
            self.data['emailaddress_set-0-email_address'] = 'user@user.com'
            self.data['emailaddress_set-0-DELETE'] = False
        if second_email:
            #fill out second email address form
            self.data['emailaddress_set-1-email_address'] = 'user1@user.com'
            self.data['emailaddress_set-1-DELETE'] = False
        if fisrt_address:
            #fill out first address form
            self.data['address_set-0-line1'] = 'Street 1'
            self.data['address_set-0-zip_code'] = '82100'
            self.data['address_set-0-city'] = 'Bratislava'
        if second_email:
            #fill out second address form
            self.data['address_set-1-line1'] = 'Street 2'
            self.data['address_set-1-zip_code'] = '82100'
            self.data['address_set-1-city'] = 'Bratislava'
            
    def check_wrong_submission(self, response, num_fields, error_message):
        u = User.objects.get(pk=self.user.pk)
        #Check if user profile is marked as completed
        self.assertFalse(u.profile_completed)
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        #Check if create profile view page was loaded again
        self.assertTemplateUsed('/auctions/account/create_profile.html')
        #Check if field errors are displayed for empty required fields of all forms
        self.assertEqual(len(re.findall(error_message, response)), num_fields)
        
    def check_valid_submission(self, response):
        u = User.objects.get(pk=self.user.pk)
        #Check if user profile is marked as completed
        self.assertTrue(u.profile_completed)
        #Check if user was redirected to profile page
        self.assertRedirects(response, reverse('auctions:profile', args=[self.user.pk]), 
                                status_code=302, target_status_code=200,
                                fetch_redirect_response=True)
        #Check if success message is displayed
        self.assertContains(response, "You profile was successfully created!")
            
        
    def test_create_profile_view_url(self):
        """
        Tests url is reachable, url naming works and correct template is used.
        """
        #Issue a GET request
        response = self.client.get('/create_profile/' + str(self.user.pk) + '/')
        
        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
    def test_create_profile_view_url_name(self):
        """
        Test checks url naming works and correct template
        is used.
        """
        #Issue a GET request
        response = self.client.get(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ))

        #Check if response code is 200 OK
        self.assertEqual(response.status_code, 200)

        #Check correct template is used
        self.assertTemplateUsed('/auctions/account/create_profile.html')
        
    def test_create_profile_form_formsets_displayed(self):
        """
        Test that form and formsets required to complete profile
        are displayed.
        """
        #Issue a GET request
        response = self.client.get(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ))

        #Check form is in content 
        self.assertContains(response, 
                '<form action="/create_profile/' + str(self.user.pk) + '/" method="post">'
                )
        #Check user full name form is in content 
        self.assertContains(response, 'id_first_name')
        #Check the first form of email formset is in content 
        self.assertContains(response, 'emailaddress_set-0')
        #Check the second form of email formset is in content 
        self.assertContains(response, 'emailaddress_set-1')
        #Check the first form of address formset is in content 
        self.assertContains(response, 'address_set-0')
        #Check the second form of address formset is in content 
        self.assertContains(response, 'address_set-1')
        
    def test_create_profile_post_empty_data(self):
        """
        Test if user is returned to create profile view page while trying 
        to submit the form with empty data in full name form and formset
        forms. Due to Django logic even forms in a formset marked as 
        deleted will show error on empty but required fields if the whole
        submission is not valid.
        """
        #Issue a POST request
        response = self.client.post(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ), self.data)
        self.check_wrong_submission(response, 11, "This field is required.")
        
    def test_create_profile_post_full_name_and_empty_formsets(self):
        """
        Test if user is returned on create profile page if full_name form
        is valid but the first address form is not filled.
        """
        #prepare data set
        self.set_data(full_name=True)
        #Issue a POST request
        response = self.client.post(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ), self.data)
        self.check_wrong_submission(response, 8, "This field is required.")
        
    def test_create_profile_post_empty_full_name_and_address1(self):
        """
        Test if user is returned on create profile page if full_name form
        is not filled and first address form is filled.
        """
        #prepare data set
        self.set_data(first_address=True)
        #Issue a POST request
        response = self.client.post(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ), self.data)
        self.check_wrong_submission(response, 8, "This field is required.")
        
    def test_create_profile_post_full_name_and_address1(self):
        """
        Test if profile is successfully created on submission of
        full name and first address forms (other forms in formsets
        are marked as 'deleted'.
        """
        #Prepare data set
        self.set_data(full_name=True, first_address=True)
        #Issue a POST request
        response = self.client.post(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ), self.data,
                                        follow=True)
        self.check_valid_submission(response)
        
    def test_create_profile_empty_first_email(self):
        """
        Test if user is returned on create profile page if full_name form
        is not filled and first address form is filled.
        """
        #Prepare data set
        self.set_data(full_name=True, first_address=True)
        self.data['emailaddress_set-0-DELETE'] = False
        #Issue a POST request
        response = self.client.post(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ), self.data)
        self.check_wrong_submission(response, 8, "This field is required.")
        
    def test_create_profile_post_full_name_email1_address1(self):
        """
        Test if profile is successfully created on submission of
        full name and first address forms (other forms in formsets
        are marked as 'deleted'.
        """
        #Prepare data set
        self.set_data(full_name=True, first_email=True, first_address=True)
        #Issue a POST request
        response = self.client.post(reverse(
                                        'auctions:create_profile', 
                                        args=[self.user.pk,]
                                        ), self.data,
                                        follow=True)
        self.check_valid_submission(response)
        
        
class TestSeleniumCreateProfileView(StaticLiveServerTestCase):
    """
    Tests profile completion process including check of JS powered UI
    elements works as expected.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        #workaround to avoid 'connection refused' error if there is non-finished webdriver instance
        for c in range(5):
            try:
                binary = FirefoxBinary('/usr/lib/firefox/firefox')
                cls.selenium = webdriver.Firefox(firefox_binary=binary)
                cls.selenium.implicitly_wait(10)
                break
            except WebDriverException:
                PROCNAME = "geckodriver"
                for proc in psutil.process_iter():
                    if proc.name() == PROCNAME:
                        proc.kill()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()    
    
    def setUp(self):
        """
        Prepare data common for all tests in this class.
        """
        User.objects.create_user("test_user1", "", 'Pass1')
        self.user = User.objects.get(username='test_user1')
        if self.user is not None:
            self.client.force_login(self.user)
        self.cookie = self.client.cookies['sessionid']
        
        #selenium initialization
        self.selenium.get(self.live_server_url + '/')
        self.selenium.add_cookie({'name': 'sessionid', 'value': self.cookie.value, 'secure': False, 'path': '/'})
        self.selenium.refresh()
        #open create profile page in browser
        self.selenium.get("%s%s%d" % (
                                    self.live_server_url, 
                                    "/create_profile/", 
                                    self.user.pk
                                    ))

    def test_create_profile_add_remove_email_forms(self):
        """
        Test that JS functions to add and remove email address forms
        work as intended.
        """
        #check if email forms are not displayed and marked as 'deleted' 
        #by default
        TODO
        #add first email form                        
        add_email_button = self.selenium.find_element_by_id("addEmail")
        add_email_button.click()
        #check first email form is displayed and not marked as 'deleted'
        TODO
        #add the second email form
        add_email_button.click()
        #check second email form is displayed and not marked as 'deleted'
        TODO
        #remove first email form
        TODO
        #check if first email form is not displayed and marked 'deleted'
        TODO
        #remove second email form
        TODO
        #check if second email form is not displayed and marked 'deleted'
        TODO
        
    def test_create_profile_add_remove_second_address_form(self):
        """
        Test that JS functions to add and remove second address form
        work as intended.
        """
        #check if first addres form is displayed and not marked 'deleted'
        #by default
        TODO
        #check if second address form is not displayed and marked as deleted
        #by default
        TODO
        #add an additional address form and left it empty                         
        add_address_button = self.selenium.find_element_by_id("addAddress")
        add_address_button.click()
        #check if second address form is displayed and not marked as 'deleted'
        TODO
        #remove second address form
        TODO
        #check if second address form is not displayed and marked 'deleted'
        TODO
                                 
    def test_create_profile_add_remove_forms(self):
        """
        Test JS functionality to add and delete forms in formsets.
        """
        #fill user full name form and address_formset form 0
        self.sel_test_fill_name_form()
        self.sel_test_fill_address_form()
        
        #check the first and the second email formsa are not displayed
        email_form_1 = self.selenium.find_element_by_id("email-address-form-0")
        email_form_2 = self.selenium.find_element_by_id("email-address-form-1")
        self.assertFalse(email_form_1.is_displayed())
        self.assertFalse(email_form_2.is_displayed())
        #add email form - the form should be unmarked from deletion on button click                           
        add_email_button = self.selenium.find_element_by_id("addEmail")
        add_email_button.click()
        #check the email form-0 is displayed
        self.assertTrue(email_form_1.is_displayed())
        #check that email_form-0 is not marked as deleted and 'input[type=checkbox]' is hidden'
        delete_email_checkbox = self.selenium.find_element_by_id("id_emailaddress_set-0-DELETE")
        self.assertFalse(delete_email_checkbox.is_displayed())
        self.assertFalse(delete_email_checkbox.is_selected())
        #check label (Remove button) is hidden in address form 0
        delete_address_0_label = self.selenium.find_element_by_xpath("//table[@id='address-form-0']/tr[td[input[@id='id_address_set-0-DELETE']]]")
        self.assertFalse(delete_address_0_label.is_displayed()) 
        
        #add second email form - the form should be unmarked from deletion on button click                           
        add_email_button.click()
        #check the email form-0 is displayed
        self.assertTrue(email_form_2.is_displayed())
        #check that email_form-1 is not marked as deleted and 'input[type=checkbox]' is hidden
        delete_email_checkbox1 = self.selenium.find_element_by_id("id_emailaddress_set-1-DELETE")
        self.assertFalse(delete_email_checkbox1.is_displayed())        
        self.assertFalse(delete_email_checkbox1.is_selected())
        
        #check address form-0 is displayed
        address_from_1 = self.selenium.find_element_by_id("address-form-0")
        self.assertTrue(address_form_1.is_displayed())
        
        #check address form-1 is not displayed
        address_form_2 = self.selenium.find_element_by_id("address-form-1")
        self.assertFalse(address_form_2.is_displayed())
        
        #add an additional address form                         
        add_address_button = self.selenium.find_element_by_id("addAddress")
        add_address_button.click()
        #check address form-1 is now displayed
        self.assertTrue(address_form_2.is_displayed())
        #check that address_form-1 is not marked as deleted
        delete_address_checkbox1 = self.selenium.find_element_by_id("id_address_set-1-DELETE")
        self.assertFalse(delete_address_checkbox.is_selected())
        self.assertFalse(delete_address_checkbox.is_displayed())
        
        #remove the second address form
        remove_buttons[2].click()
        #check that address_form-1 is marked as deleted
        self.assertTrue(delete_address_checkbox.is_selected())
        
        #remove the second email form
        remove_buttons[1].click()
        #check that email_form-1 is marked as deleted
        self.assertTrue(delete_email_checkbox2.is_selected())
        
        #remove the first email form
        remove_buttons[0].click()
        #check that email_form-0 is marked as deleted
        self.assertTrue(delete_email_checkbox2.is_selected())
        
        #check profile created
        self.check_valid_submission()

                                 
    def test_create_profile_types_switch(self):
        """
        Test JS functionality to switch types of email and addresses.
        """
        #add two email forms                           
        add_email_button = self.selenium.find_element_by_id("addEmail")
        add_email_button.click()
        add_email_button.click()
        #check initial types of email forms
        email_form_0_type_selector = self.selenium.find_element_by_id("id_emailaddress_set-0-email_type")
        email_form_1_type_selector = self.selenium.find_element_by_id("id_emailaddress_set-1-email_type")
        self.assertEqual(email_form_0_type_selector.get_attribute("value"), "CT")
        self.assertEqual(email_form_1_type_selector.get_attribute("value"), "PT")
        #change type of the first email form and check if a type of the second form changed as well
        Select(email_form_0_type_selector).select_by_value("PT")
        self.assertEqual(email_form_1_type_selector.get_attribute("value"), "CT")
        #try to change type of the second email form and check if types of both forms were not changed
        Select(email_form_1_type_selector).select_by_value("PT")
        self.assertEqual(email_form_0_type_selector.get_attribute("value"), "PT")
        self.assertEqual(email_form_1_type_selector.get_attribute("value"), "CT")
        
        #add an additional address form                         
        add_address_button = self.selenium.find_element_by_id("addAddress")
        add_address_button.click()
        #check initial types of address forms
        address_form_0_type_selector = self.selenium.find_element_by_id("id_address_set-0-address_type")
        address_form_1_type_selector = self.selenium.find_element_by_id("id_address_set-1-address_type")
        self.assertEqual(address_form_0_type_selector.get_attribute("value"), "DL")
        self.assertEqual(address_form_1_type_selector.get_attribute("value"), "BL")
        #change type of the first address form and check if a type of the second form changed as well
        Select(address_form_0_type_selector).select_by_value('BL')
        self.assertEqual(address_form_1_type_selector.get_attribute("value"), "DL")
        #change type of the second address form and check if types of both forms were not changed
        Select(address_form_1_type_selector).select_by_value('BL')
        self.assertEqual(address_form_0_type_selector.get_attribute("value"), "BL")
        self.assertEqual(address_form_1_type_selector.get_attribute("value"), "DL")
