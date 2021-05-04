import datetime
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.db import models


class Address(models.Model):
	
	line1 = models.CharField(max_length=100, null=True, blank=True)
	line2 = models.CharField(max_length=100, null=True, blank=True)
	zip_code = models.CharField(max_length=6, null=True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)
	country = models.CharField(max_length=100, null=True, blank=True)

class User(AbstractUser):
	
	delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL,
								null=True, blank=True, related_name="sender")
	billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL,
								null=True, blank=True, related_name="seller")
    
    
class Category(models.Model):
	
	name = models.CharField("category's title", max_length=100, unique=True)
	description = models.CharField("category's description", max_length=255, blank=True)
	
	def __str__(self):
		return self.name


class Product(models.Model):
	
	seller = models.ForeignKey(User, on_delete=models.CASCADE, 
				help_text="User who sells this product",
				related_name="products")
					
	categories = models.ManyToManyField(Category, 
				verbose_name="product's category",
				help_text="The product is included in the following categories",
				related_name="products")
				
	name = models.CharField("product's title", max_length=255, unique=True)
	description = models.CharField("product's description", max_length=1000, blank=True)
	
	def __str__(self):
		return self.name
		

def get_product_image_filename(instance, filename):
	title = instance.product.name
	slug = slugify(title)
	return "images/%s-%s" % (slug, filename)
	
class Image(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	image = models.ImageField("Product's image", 
				upload_to=get_product_image_filename,
				null=True, blank=True)
	image_url = models.URLField("URL of product's image", null=True, blank=True)	
	
class Listing(models.Model):
	
	PAYMENT = "The seller will send information about the payment to the winner within \
				2 business days after the auction end. \n\
				The winner can initiate a dispute or cancel the order if information \
				required for payment was not received from the seller in due time. \n\
				The seller has a right to cancel the order if the payment was not \
				received in due	time, amount due or due order as requested. In this \
				case the seller shall return funds received after the term / not in \
				due order to the buyer within 3	business days after their receipt. The \
				seller has a right to withdraw from the funds to be returned an amount \
				required to cover reasonable actual expenses related to the funds \
				return."
	SHIPMENT = "The product will be shipped to the auction winner within 5 business \
				days after the payment receipt. \n\
				The seller may request from the winner additional information \
				reasonably required for shipment. In this case the product will be \
				shipped within 3 business days after receipt of the requested \
				information.\n\
				The winner has a right to open a dispute and request funds' return in \
				case the product was not delivered to the winner within 45 days after \
				the payment."
	RETURN = "Return is not accepted for this auction. The product is sold AS IS."
	
	class productState(models.IntegerChoices):
		USED = 0
		NEW = 1
	
	product = models.ForeignKey(Product, on_delete=models.CASCADE,
				verbose_name="product offered in the listing",
				related_name="listings"
				)
				
	followers = models.ManyToManyField(
		User, verbose_name="users following the listing", 
		help_text="Users who add the listing in their watch lists.", 
		related_name="watchlist"
		)
	
	payment_policy = models.TextField(default=PAYMENT)
	shipment_policy = models.TextField(default=SHIPMENT)
	return_policy = models.TextField(default=RETURN)
	created_on = models.DateTimeField(auto_now_add=True)
	state = models.IntegerField("product's condition", 
				choices=productState.choices, default=productState.USED)
	start_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('1.00'), 
					help_text="Starting price for the listing in the whole Euros. Min. 1 EUR")
	start_time = models.DateTimeField(default=timezone.now)
	duration = models.DurationField("duration of the listing",
				default = datetime.timedelta(days=10),
				help_text="Duration of the listing in days. Default to 10 days.")
	cancelled = models.BooleanField(default=False)
	
	@property
	def status(self):
		if self.cancelled:
			return "cancelled"
		dt = timezone.now()
		if self.end_time < dt:
			return "ended"
		elif self.start_time > dt:
			return "not started yet"
		else:
			return "active"
	
	@property
	def end_time(self):
		return self.start_time + self.duration
		
	@property
	def max_bid(self):
		try:
			mbid = self.bids.order_by('-value')[0:1].get()
		except Bid.DoesNotExist:
			return Decimal('0.00')
		return mbid.value
				
	@property
	def winner(self):
		if self.status == "ended" or \
				self.status == "cancelled":
			bids = self.bids.all()
			if bids:
				return bids.order_by('-value')[0].bidder
		return None
		
	@property
	def get_absolute_url(self):
		return reverse('auctions:listing', args=[str(self.id)])
	
	def __str__(self):
		return f"Auction listing for {self.product.name}. \
				start time: {self.start_time}, \
				start price: {self.start_price}, \
				duration: {self.duration} days, \
				status: {self.status}." 
	
	
class Bid(models.Model):
	
	bidder = models.ForeignKey(User, on_delete=models.CASCADE,
				verbose_name="user placed the bid",
				related_name="bids")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
				verbose_name="listing to which the bid was placed",
				related_name="bids")
	value = models.DecimalField("bid amount, EUR", max_digits=8, decimal_places=2,
				default=0.00, help_text="Bid amount in Euro.")
	time = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f"User {self.bidder.name} \
				bids {self.value} at {self.time}."
		
		
class Comment(models.Model):
	
	author = models.ForeignKey(User, on_delete=models.CASCADE,
				verbose_name="user placed the comment")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
				verbose_name="listing on which the comment was left")
	content = models.CharField("comment's text", max_length=1000)
	time = models.DateTimeField(auto_now_add=True)
	
	@property
	def status(self):
		if not self.answer_set.all():
			return "pending"
		return "answered"
	
	def __str__(self):
		return f"User {self.author.name} comments on \
				auction for {self.listing.product.name} \
				at {self.time}."
				
class Answer(models.Model):
	
	respondent = models.ForeignKey(User, on_delete=models.CASCADE,
					verbose_name="seller")
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE,
					verbose_name="answered comment")
	content = models.CharField("answer's text", max_length=1000)
	time = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f"User {self.respondent.name} answered to \
				a comment of {self.comment.author.name} \
				at {self.time}."
	
