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
		
		# Create test users to use in testing
		cls.testuser1 = User.objects.create_user(
										username="test_user1",
										email="test_email1@test.com",
										password='Pass&2021',
										title="MR",
										first_name="John",
										last_name="Smith"
										)
		cls.testuser2 = User.objects.create_user(
										username="test_user2",
										email="test_email2@test.com",
										password='Pass&2021',
										title="MR",
										first_name="Ivan",
										last_name="Petrov"
										)
		# Create test users delivery addresses to use in testing
		cls.testuser1.address_set.add(Address.objects.create(
										user=cls.testuser1,
										line1="street 1",
										zip_code="99999",
										city="city"
										))
		cls.testuser2.address_set.add(Address.objects.create(
										user=cls.testuser2,
										line1="street 2",
										zip_code="99999",
										city="city"
										))
		# Create test category
		cls.category = Category.objects.create(
							name="testcategory",
							description="category for testing purposes")
		# Create test product
		cls.product = cls.category.products.create(
							name="testproduct",
							description="Product for testing purposes",
							seller = cls.testuser1
							)
							
	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()

		# Close worker
		cls.celery_worker.__exit__(None, None, None)
		
		
	def test_winner_ended_listing(self):
		testlisting1 = Listing.objects.create(
								product=CeleryTasksTestCase.product,
								duration=timedelta(seconds=5))
		bid1 = Bid.objects.create(bidder=CeleryTasksTestCase.testuser2, 
								listing=testlisting1, 
								value=Decimal('2.00'))
		sleep(6)
		
		# testing a messages were sent to both seller and buyer
		message1 = Message.objects.filter(content__contains="is the listing winner").first()
		self.assertTrue(message1)
		self.assertEqual(message1.recipient, CeleryTasksTestCase.testuser1)
		message2 = Message.objects.filter(content__contains="Congratulation! You are the winner in the Auction$ listing").first()
		self.assertTrue(message2)
		self.assertEqual(message2.recipient, CeleryTasksTestCase.testuser2)
		
	def test_no_bid_ended_listing(self):
		testlisting2 = Listing.objects.create(
								product=CeleryTasksTestCase.product,
								duration=timedelta(seconds=5))
		sleep(6)
		
		# testing a message was sent to seller
		message = Message.objects.filter(content__contains="Your listing for testproduct was ended without a winner.").first()
		self.assertTrue(message)
		self.assertEqual(message.recipient, CeleryTasksTestCase.testuser1)
        
