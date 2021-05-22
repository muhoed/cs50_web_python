from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404

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
        User.objects.create_user("test_user1", "", 'Pass1')
        User.objects.create_user("test_user2", "", 'Pass2')
        User.objects.create_user("test_user3", "", 'Pass3')
        # Create profile for test_user1
        Contact.objects.create(user=User.objects.get(username='test_user1'),
                                title='MR', first_name='Test', last_name='Testoff',
                                line1='street 1', zip_code='00000',
                                city='testcity', country='SK')   
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
        product1 = get_object_or_404(Product, id=1)
        product2 = get_object_or_404(Product, id=2)
        listing1 = Listing.objects.create(product=product1)
        listing2 = Listing.objects.create(product=product2)
        response = self.client.get(reverse('auctions:index'))
        
        #Check two listings are in context
        self.assertEqual(len(response.context['active_listings_list']), 2)
        
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
        self.assertTemplateUsed('/auctions/login.html')
    
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
        self.assertEqual(str(response.context['user']), u.username)
        
        #Check user was redirected to home page
        self.assertRedirects(response, reverse('auctions:profile'))
        
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
        self.assertTemplateUsed('/auctions/register.html')
        
    def test_register_form_displayed(self):
        """
        Test that register form is displayed.
        """
        #Issue a GET request
        response = self.client.get(reverse('auctions:register'))

        #Check register form is in content 
        self.assertContains(response, '<form')
        
    def test_register_user_empty_data(self):
        """
        Test that register view returns error if no data are provided.
        """
        #Issue a POST request with empty data
        response = self.client.post(reverse('auctions:register'),
                                    {'username':'', 'email':'', 'password':'',
                                        'confirmation':'', 'title':'', 
                                        'first_name':'', 'last_name':'',
                                        'line1':'', 'zip_code':'', 'city':'',
                                        'country':''})

        #Check the page is loaded 
        self.assertEqual(response.status_code, 200)
        #Check errors are displayed by the form
        self.assertFormError(response, 'user_form', 
                                'username', 'This field is required.')
        self.assertFormError(response, 'user_form', 
                                'password1', 'This field is required.')
        self.assertFormError(response, 'user_form', 
                                'password2', 'This field is required.')
        self.assertFormError(response, 'contact_form', 
                                'title', 'This field is required.')
        self.assertFormError(response, 'contact_form', 
                                'first_name', 'This field is required.')
        self.assertFormError(response, 'contact_form', 
                                'last_name', 'This field is required.')
        self.assertFormError(response, 'contact_form', 
                                'line1', 'This field is required.')
        self.assertFormError(response, 'contact_form', 
                                'zip_code', 'This field is required.')
        self.assertFormError(response, 'contact_form', 
                                'city', 'This field is required.')
        self.assertFormError(response, 'contact_form', 
                                'country', 'This field is required.')
        
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
        self.assertFormError(response, 'user_form', 
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
                                                    'password2':'111',
                                                    'title':'MR',
                                                    'first_name':'test',
                                                    'last_name':'user',
                                                    'line1':'street 1',
                                                    'zip_code':'00000',
                                                    'city':'town',
                                                    'country':'SK'})
        
        #Check errors are displayed by the form
        self.assertFormError(response, 'user_form',
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
        self.assertFormError(response, 'user_form',
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
                                                    'password2':'Pass&2021',
                                                    'title':'MR',
                                                    'line1':'street 1',
                                                    'zip_code':'00000',
                                                    'city':'town',
                                                    'country':'SK'})

        #Check errors are displayed by the form
        self.assertFormError(
                    response, 'user_form', 'username', 
                    'A user with that username already exists.'
                    )
        
    def test_register_user_right_data(self):
        """
        Test that user is logged in and redirected to home page when 
        form is filled correctly.
        """
        #Issue a POST request with correct and complete data
        response = self.client.post(reverse('auctions:register'),
                                                    {'username':'test_user4',
                                                    'email':'test@test.com',
                                                    'password1':'Pass&2021',
                                                    'password2':'Pass&2021',
                                                    'title':'MR',
                                                    'first_name':'test',
                                                    'last_name':'user',
                                                    'line1':'street 1',
                                                    'zip_code':'00000',
                                                    'city':'town',
                                                    'country':'SK'},
                                                    follow=True)
        
        #Check user was redirected to home page
        self.assertRedirects(response, reverse('auctions:index'))#, 
                                #status_code=302, target_status_code=200,
                                #fetch_redirect_response=True)
        self.assertTemplateUsed('/auctions/index.html')
        #self.assertEqual(response.context, "You were successfully registered and logged in.")                                            
        #Check user in session is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        #Check if user data are correct
        u = User.objects.get(username='test_user4')
        self.assertEqual(response.context['user'].username, u.username)
        
