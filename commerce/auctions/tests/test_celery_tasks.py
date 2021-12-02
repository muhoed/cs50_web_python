from datetime import timedelta
from time import sleep
from decimal import Decimal

from celery.contrib.testing.worker import start_worker
from django.test import SimpleTestCase

from commerce.celery import celery_app
from auctions.models import User, Address, Product, Category, Listing, Message, Bid


class CeleryTasksTestCase(SimpleTestCase):
	"""
	Testing background tasks handled by Celery workers.
	"""
	databases = '__all__'

	@classmethod
	def setUpClass(cls):
		super().setUpClass()

		# Start up celery worker
		cls.celery_worker = start_worker(celery_app, perform_ping_check=False)
		cls.celery_worker.__enter__()
		
	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()

		# Close worker
		cls.celery_worker.__exit__(None, None, None)
		
	def setUp(self):
		# Create test users to use in testing
		self.testuser1 = User.objects.create_user(
										username="test_user1",
										email="test_email1@test.com",
										password='Pass&2021',
										title="MR",
										first_name="John",
										last_name="Smith"
										)
		self.testuser2 = User.objects.create_user(
										username="test_user2",
										email="test_email2@test.com",
										password='Pass&2021',
										title="MR",
										first_name="Ivan",
										last_name="Petrov"
										)
		# Create test users delivery addresses to use in testing
		self.testuser1.address_set.add(Address.objects.create(
										user=self.testuser1,
										line1="street 1",
										zip_code="99999",
										city="city"
										))
		self.testuser2.address_set.add(Address.objects.create(
										user=self.testuser2,
										line1="street 2",
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
							seller = self.testuser1
							)
		
	def test_winner_ended_listing(self):
		testlisting = Listing.objects.create(
								product=self.product,
								duration=timedelta(seconds=5))
		bid1 = Bid.objects.create(bidder=self.testuser2, 
								listing=testlisting, 
								value=Decimal('2.00'))
		sleep(10)
		
		# testing a messages were sent to both seller and buyer
		message1 = Message.objects.filter(content__contains="The user test_user2 placed the highest bid and is the listing winner").first()
		self.assertTrue(message1)
		self.assertEqual(message.recipient, self.testuser1)
		message2 = Message.objects.filter(content__contains="Congratulation! You are the winner in the Auction$ listing").first()
		self.assertTrue(message2)
		self.assertEqual(message2.recipient, self.testuser2)
        
