from django.test import TestCase
from django.http import HttpRequest

from auctions.forms import *
from auctions.models import *


class RegisterFormTest(TestCase):
    """
    Testing RigisterForm core functionality.
    """

    def setUp(self):
        self.form = RegisterForm()

    def test_empty_form(self):
        self.assertIn("email", self.form.fields)
        
    def test_post_data_to_form(self):
        request = HttpRequest()
        request.POST = {
            'title': 'MR',
            'first_name': 'User',
            'last_name': 'Testoff',
            'username': 'testuser',
            'email': 'test@email.test',
            'password1': 'Pass&2021',
            'password2': 'Pass&2021'
        }
        
        form = RegisterForm(request.POST)
        form.save()
        self.assertEqual(User.objects.count(), 1)
		
	
