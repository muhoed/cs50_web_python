import datetime
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.db import models


class User(AbstractUser):
	
	TITLE_CHOICES = [
		('MR', 'Mr.'),
		('MRS', 'Mrs.'),
		('MS', 'Ms.'),
	]
	
	title = models.CharField(max_length=3, choices=TITLE_CHOICES, null=True, blank=False)
	first_name = models.CharField(max_length=50, null=True, blank=False)
	last_name = models.CharField(max_length=50, null=True, blank=False)
	email = models.EmailField(_('email address'), unique=True, null=False, blank=False)
	profile_completed = models.BooleanField(default=False)
	
	@property
	def full_name(self):
		if self.title and self.first_name and self.last_name:
			return f'%s %s %s' % (self.get_title_display(), self.first_name, self.last_name)
		return f'%s' % {self.username}
	
	def get_absolute_url(self):
		return reverse('auctions:profile', kwargs={'pk': self.pk})
	
	def __str__(self):
	    return f'%s' % (self.full_name)
	    

class EmailAddress(models.Model):
	
	TYPE_CHOICES = [
		('CT', 'Contact'),
		('PT', 'Payment'),
	]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	email_address = models.EmailField()
	email_type = models.CharField(max_length=2, choices=TYPE_CHOICES, 
									blank=False, default='CT')
									
	def __str__(self):
		return f'Email address for %s: %s' % (self.get_email_type_display().lower(),
															self.email_address
															)
	
	
class Address(models.Model):
	
	TYPE_CHOICES = [
		('DL', 'Delivery address'),
		('BL', 'Billing address'),
	]
	
	COUNTRY_CHOICES = [
		('AD', _('Andorra')), ('AE', _('United Arab Emirates')), ('AF', _('Afghanistan')),
		('AG', _('Antigua & Barbuda')), ('AI', _('Anguilla')), ('AL', _('Albania')),
		('AM', _('Armenia')), ('AN', _('Netherlands Antilles')), ('AO', _('Angola')),
		('AQ', _('Antarctica')), ('AR', _('Argentina')), ('AS', _('American Samoa')),
		('AT', _('Austria')),
		('AU', _('Australia')),
		('AW', _('Aruba')),
		('AZ', _('Azerbaijan')),
		('BA', _('Bosnia and Herzegovina')),
		('BB', _('Barbados')),
		('BD', _('Bangladesh')),
		('BE', _('Belgium')),
		('BF', _('Burkina Faso')),
		('BG', _('Bulgaria')),
		('BH', _('Bahrain')),
		('BI', _('Burundi')),
		('BJ', _('Benin')),
		('BM', _('Bermuda')),
		('BN', _('Brunei Darussalam')),
		('BO', _('Bolivia')),
		('BR', _('Brazil')),
		('BS', _('Bahama')),
		('BT', _('Bhutan')),
		('BV', _('Bouvet Island')),
		('BW', _('Botswana')),
		('BY', _('Belarus')),
		('BZ', _('Belize')),
		('CA', _('Canada')),
		('CC', _('Cocos (Keeling) Islands')),
		('CF', _('Central African Republic')),
		('CG', _('Congo')),
		('CH', _('Switzerland')),
		('CI', _('Ivory Coast')),
		('CK', _('Cook Iislands')),
		('CL', _('Chile')),
		('CM', _('Cameroon')),
		('CN', _('China')),
		('CO', _('Colombia')),
		('CR', _('Costa Rica')),
		('CU', _('Cuba')),
		('CV', _('Cape Verde')),
		('CX', _('Christmas Island')),
		('CY', _('Cyprus')),
		('CZ', _('Czech Republic')),
		('DE', _('Germany')),
		('DJ', _('Djibouti')),
		('DK', _('Denmark')),
		('DM', _('Dominica')),
		('DO', _('Dominican Republic')),
		('DZ', _('Algeria')),
		('EC', _('Ecuador')),
		('EE', _('Estonia')),
		('EG', _('Egypt')),
		('EH', _('Western Sahara')),
		('ER', _('Eritrea')),
		('ES', _('Spain')),
		('ET', _('Ethiopia')),
		('FI', _('Finland')),
		('FJ', _('Fiji')),
		('FK', _('Falkland Islands (Malvinas)')),
		('FM', _('Micronesia')),
		('FO', _('Faroe Islands')),
		('FR', _('France')),
		('FX', _('France, Metropolitan')),
		('GA', _('Gabon')),
		('GB', _('United Kingdom (Great Britain)')),
		('GD', _('Grenada')),
		('GE', _('Georgia')),
		('GF', _('French Guiana')),
		('GH', _('Ghana')),
		('GI', _('Gibraltar')),
		('GL', _('Greenland')),
		('GM', _('Gambia')),
		('GN', _('Guinea')),
		('GP', _('Guadeloupe')),
		('GQ', _('Equatorial Guinea')),
		('GR', _('Greece')),
		('GS', _('South Georgia and the South Sandwich Islands')),
		('GT', _('Guatemala')),
		('GU', _('Guam')),
		('GW', _('Guinea-Bissau')),
		('GY', _('Guyana')),
		('HK', _('Hong Kong')),
		('HM', _('Heard & McDonald Islands')),
		('HN', _('Honduras')),
		('HR', _('Croatia')),
		('HT', _('Haiti')),
		('HU', _('Hungary')),
		('ID', _('Indonesia')),
		('IE', _('Ireland')),
		('IL', _('Israel')),
		('IN', _('India')),
		('IO', _('British Indian Ocean Territory')),
		('IQ', _('Iraq')),
		('IR', _('Islamic Republic of Iran')),
		('IS', _('Iceland')),
		('IT', _('Italy')),
		('JM', _('Jamaica')),
		('JO', _('Jordan')),
		('JP', _('Japan')),
		('KE', _('Kenya')),
		('KG', _('Kyrgyzstan')),
		('KH', _('Cambodia')),
		('KI', _('Kiribati')),
		('KM', _('Comoros')),
		('KN', _('St. Kitts and Nevis')),
		('KP', _('Korea, Democratic People\'s Republic of')),
		('KR', _('Korea, Republic of')),
		('KW', _('Kuwait')),
		('KY', _('Cayman Islands')),
		('KZ', _('Kazakhstan')),
		('LA', _('Lao People\'s Democratic Republic')),
		('LB', _('Lebanon')),
		('LC', _('Saint Lucia')),
		('LI', _('Liechtenstein')),
		('LK', _('Sri Lanka')),
		('LR', _('Liberia')),
		('LS', _('Lesotho')),
		('LT', _('Lithuania')),
		('LU', _('Luxembourg')),
		('LV', _('Latvia')),
		('LY', _('Libyan Arab Jamahiriya')),
		('MA', _('Morocco')),
		('MC', _('Monaco')),
		('MD', _('Moldova, Republic of')),
		('MG', _('Madagascar')),
		('MH', _('Marshall Islands')),
		('ML', _('Mali')),
		('MN', _('Mongolia')),
		('MM', _('Myanmar')),
		('MO', _('Macau')),
		('MP', _('Northern Mariana Islands')),
		('MQ', _('Martinique')),
		('MR', _('Mauritania')),
		('MS', _('Monserrat')),
		('MT', _('Malta')),
		('MU', _('Mauritius')),
		('MV', _('Maldives')),
		('MW', _('Malawi')),
		('MX', _('Mexico')),
		('MY', _('Malaysia')),
		('MZ', _('Mozambique')),
		('NA', _('Namibia')),
		('NC', _('New Caledonia')),
		('NE', _('Niger')),
		('NF', _('Norfolk Island')),
		('NG', _('Nigeria')),
		('NI', _('Nicaragua')),
		('NL', _('Netherlands')),
		('NO', _('Norway')),
		('NP', _('Nepal')),
		('NR', _('Nauru')),
		('NU', _('Niue')),
		('NZ', _('New Zealand')),
		('OM', _('Oman')),
		('PA', _('Panama')),
		('PE', _('Peru')),
		('PF', _('French Polynesia')),
		('PG', _('Papua New Guinea')),
		('PH', _('Philippines')),
		('PK', _('Pakistan')),
		('PL', _('Poland')),
		('PM', _('St. Pierre & Miquelon')),
		('PN', _('Pitcairn')),
		('PR', _('Puerto Rico')),
		('PT', _('Portugal')),
		('PW', _('Palau')),
		('PY', _('Paraguay')),
		('QA', _('Qatar')),
		('RE', _('Reunion')),
		('RO', _('Romania')),
		('RU', _('Russian Federation')),
		('RW', _('Rwanda')),
		('SA', _('Saudi Arabia')),
		('SB', _('Solomon Islands')),
		('SC', _('Seychelles')),
		('SD', _('Sudan')),
		('SE', _('Sweden')),
		('SG', _('Singapore')),
		('SH', _('St. Helena')),
		('SI', _('Slovenia')),
		('SJ', _('Svalbard & Jan Mayen Islands')),
		('SK', _('Slovakia')),
		('SL', _('Sierra Leone')),
		('SM', _('San Marino')),
		('SN', _('Senegal')),
		('SO', _('Somalia')),
		('SR', _('Suriname')),
		('ST', _('Sao Tome & Principe')),
		('SV', _('El Salvador')),
		('SY', _('Syrian Arab Republic')),
		('SZ', _('Swaziland')),
		('TC', _('Turks & Caicos Islands')),
		('TD', _('Chad')),
		('TF', _('French Southern Territories')),
		('TG', _('Togo')),
		('TH', _('Thailand')),
		('TJ', _('Tajikistan')),
		('TK', _('Tokelau')),
		('TM', _('Turkmenistan')),
		('TN', _('Tunisia')),
		('TO', _('Tonga')),
		('TP', _('East Timor')),
		('TR', _('Turkey')),
		('TT', _('Trinidad & Tobago')),
		('TV', _('Tuvalu')),
		('TW', _('Taiwan, Province of China')),
		('TZ', _('Tanzania, United Republic of')),
		('UA', _('Ukraine')),
		('UG', _('Uganda')),
		('UM', _('United States Minor Outlying Islands')),
		('US', _('United States of America')),
		('UY', _('Uruguay')),
		('UZ', _('Uzbekistan')),
		('VA', _('Vatican City State (Holy See)')),
		('VC', _('St. Vincent & the Grenadines')),
		('VE', _('Venezuela')),
		('VG', _('British Virgin Islands')),
		('VI', _('United States Virgin Islands')),
		('VN', _('Viet Nam')),
		('VU', _('Vanuatu')),
		('WF', _('Wallis & Futuna Islands')),
		('WS', _('Samoa')),
		('YE', _('Yemen')),
		('YT', _('Mayotte')),
		('YU', _('Yugoslavia')),
		('ZA', _('South Africa')),
		('ZM', _('Zambia')),
		('ZR', _('Zaire')),
		('ZW', _('Zimbabwe')),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	line1 = models.CharField(max_length=100)
	line2 = models.CharField(max_length=100, null=True, blank=True)
	zip_code = models.CharField(max_length=6)
	city = models.CharField(max_length=100)
	country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, 
									blank=False, default='SK')
	address_type = models.CharField(max_length=2, choices=TYPE_CHOICES,
										blank=False, default='DL')
	
	def __str__(self):
		if self.line2:
			line2 = ", " + self.line2
		else:
			line2 = ''
		return f'%s: %s%s, %s %s, %s' % (self.get_address_type_display(),
														self.line1, line2,
														self.zip_code, self.city,
														self.get_country_display()
														)
	   
    
    
class Category(models.Model):
	
	name = models.CharField("category's title", max_length=100, unique=True)
	description = models.CharField("category's description", max_length=255, blank=True)
	
	@property
	def get_absolute_url(self):
		return reverse('auctions:category', args=[int(self.id)])
		
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

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
		

def get_product_image_filename(instance, filename):
	title = instance.product.name
	slug = slugify(title)
	return "images/%s-%s" % (slug, filename)
	
class Image(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	#image = models.ImageField("Product's image", 
	#			upload_to=get_product_image_filename,
	#			null=True, blank=True)
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
    state = models.IntegerField("product's condition", 
                choices=productState.choices, default=productState.USED)
    start_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('1.00'), 
                    help_text="Starting price for the listing in the whole Euros. Min. 1 EUR")
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.DurationField("duration of the listing",
                default = datetime.timedelta(days=10),
                help_text="Duration of the listing in days. Default to 10 days.")
    cancelled_on = models.DateTimeField(null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
	
    @property
    def status(self):
        if self.cancelled_on:
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
        return reverse('auctions:listing', args=[int(self.id)])

    def __str__(self):
        return f"Auction listing for {self.product.name}. \
                start time: {self.start_time}, \
                start price: {self.start_price}, \
                highest bid: {self.max_bid}, \
                duration: {self.duration}, \
                status: {self.status}." 
	
	
class Bid(models.Model):
	
	bidder = models.ForeignKey(User, on_delete=models.CASCADE,
				verbose_name="user placed the bid",
				related_name="user_bids")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
				verbose_name="listing to which the bid was placed",
				related_name="bids")
	value = models.DecimalField("bid amount, EUR", max_digits=8, decimal_places=2,
				default=0.00, help_text="Bid amount in Euro.")
	time = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f"User {self.bidder.username} \
				bidded {self.value} at {self.time}."
		
		
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
	
