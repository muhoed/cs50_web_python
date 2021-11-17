from datetime import datetime
import json
import os

from django.conf import settings as conf_settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.templatetags.static import static
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.db.models import (F, Q, Max, Case, When, Value, OuterRef, Exists,
                                Count, Subquery, ExpressionWrapper, DateTimeField)
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.views.decorators.cache import never_cache
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.template import loader

from .models import *
from .forms import *



#Django class-based views are used instead of default authorisation 
#function-based views included in the project templates.


class CorrectUserTestMixin(UserPassesTestMixin):
    """
    Checks if the logged-in user tries to access her/his own account
    information. Can be used only in CBVs receiving User model instance
    'pk' as a parameter.
    """
    def test_func(self):
        """ Check user accesses her/his own profile. """
        if "user_pk" in self.kwargs:
            pk = self.kwargs["user_pk"]
        else:
            pk = self.kwargs["pk"]
        return (get_object_or_404(User, pk=pk) == self.request.user)
        
    def handle_no_permission(self):
        """ If user attempts to get access to other user's profile redirect her/him
        to home page and show her/him an access denied message. """
        if self.raise_exception or self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return render(self.request, 'auctions/index.html')
        return redirect(reverse('auctions:login'))


class UserLoginView(LoginView):
    """
    User log in interface. Redirects to the 'next' page if defined or to 
    the user's account page.
    """
    
    def get_success_url(self):
        url = self.get_redirect_url()
        return url or reverse('auctions:profile', kwargs={'pk':self.request.user.id})

class UserRegisterView(CreateView):
    """
    Registers a new user.
    """
    model = User
    form_class = RegisterForm
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class(request.POST)
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.is_active = False
            self.object.save()
            request.session["newuser"]=self.object.pk
            return redirect("auctions:registration_confirm")
        else:
            return self.render_to_response(self.get_context_data(form=form))
        

class RegistrationConfirmView(TemplateView):
    """
    In production version an email with registration confirmation link 
    to be sent to an user using the same underlying logic as Django password 
    reset workflow has.
    In this student's project version the view shows respective notification 
    with the activation link on the screen upon registration.
    """
    success_url = reverse_lazy('auctions:registration_complete')
    token_generator = default_token_generator
    subject_template_name = "auctions/auth/emails/account_activation_subject.txt"
    email_template_name = "auctions/auth/emails/account_activation_email.html"
    from_email = None
    to_email = None
    html_email_template_name = None
    use_https = False
    extra_context = None
    extra_email_context = None
        
    def get(self, request, *args, **kwargs):
        if request.session["newuser"]:
            user = User.objects.get(pk=request.session["newuser"])
            #protocol = 'http'
            protocol = 'https' if self.use_https else 'http'
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = self.token_generator.make_token(user)
            self.send_mail(
                    protocol=protocol, site_name=site_name, 
                    domain=domain, uid=uid, token=token, user=user
                    )
            return render(request, self.template_name, {
                                                'uid':uid, 'topic':'regactivate', 
                                                'token':token, 'title': self.extra_context['title']})
        return redirect(reverse('auctions:register'))
        
    def send_mail(self, protocol, site_name, domain, uid, token, user):
        """
        Generate a one-use only link for activate account and send it to the
        user.
        """
        user_email = user.email
        context = {
            'email': user_email,
            'domain': domain,
            'site_name': site_name,
            'uid': uid,
            'user': user,
            'token': token,
            'protocol': protocol,
            **(self.extra_email_context or {}),
        }
        
        #Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        #Use FileEmailBackend if set in settings
        
        subject = loader.render_to_string(self.subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(self.email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, self.from_email, [user_email])
        if self.html_email_template_name is not None:
            html_email = loader.render_to_string(self.html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()
        
INTERNAL_RESET_SESSION_TOKEN = '_activate_user_token'
        
class RegistrationCompleteView(TemplateView):
    """
    Activates newly registered user.
    """
    token_generator = default_token_generator
    reset_url_token = 'activate-user'
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if 'uidb64' not in kwargs or 'token' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )
        
        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, activate the user and show confirmation.
                    self.user.is_active=True
                    self.user.save()
                    self.validlink = True
                    return render(self.request, self.template_name, self.get_context_data())
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # account activation page at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Unsuccessful account activation" page.
        return self.render_to_response(self.get_context_data())
        
    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except:
            user = None
        return user
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'validlink': False,
            })
        return context
    

class UserPasswordResetView(PasswordResetView):
    
    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        
        #save 'uid' used as a file uniq identifier by file email backend to session
        email_backend_type = conf_settings.EMAIL_BACKEND.rsplit(".", 1)[1]
        if email_backend_type == "FileEmailBackend" and form.uid:
            self.request.session["uid"] = form.uid
        
        return HttpResponseRedirect(self.get_success_url())
    
    
def get_message_content(request):
    """
    Simple function-based API to retrieve a file names of email message files 
    generated by Django file email backend.
    Assumes that a path to files is stored in EMAIL_FILE_PATH variable in 
    settings.py and filename format is '[uid]-[topic]-[timestamp].log'.
    Parameters:
    <uid> (required) - base64 encoded string, current user pk,
    <topic> (optional) - string, email message subject not containing 
    spaces and '-',
    <start>, <end> (optional) - strings, start and end dates of selected period
    in format '%Y-%m-%d'.
    Return:
    JSONified list of triples of filename parts: [uid, topic. timestamp].
    """
    try:
        uid = request.GET.__getitem__('uidb64')
    except:
        return HttpResponseBadRequest("Missed <uidb64> parameter.")
        
    topic = request.GET.get('topic', None)
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    
    path = conf_settings.EMAIL_FILE_PATH
    file_list = os.listdir(path)
    result = []
    for fname in file_list:
        filename = fname.split(".")
        result.append(filename[0].split("_"))
        
    if start and end:
        result = [
            select for select in result 
            if datetime.timestamp(datetime.strptime(select[2], '%Y%m%d-%H%M%S')) >= datetime.timestamp(datetime.strptime(start, '%Y-%m-%d')) 
            and datetime.timestamp(datetime.strptime(select[2], '%Y%m%d-%H%M%S')) <= datetime.timestamp(datetime.strptime(end, '%Y-%m-%d'))
            ]
        
    if topic:
        result = [select for select in result if select[1] == topic]
         
    result = [select for select in result if select[0] == uid]

    result.sort(
            key=lambda res: datetime.datetime.timestamp(
                                            datetime.datetime.strptime(
                                                                res[2], 
                                                                '%Y%m%d-%H%M%S'
                                                                )
                                            ),
                                            reverse=True
            )
            
    result = ["media/emails/" + res[0] + "_" + res[1] + "_" + res[2] + ".log" for res in result]
        
    return JsonResponse(result, safe=False)
    
            
class ProfileView(LoginRequiredMixin, CorrectUserTestMixin, UpdateView):
    """
    Creates profile for newly registered user. Updates existing profile. 
    """
    model = User
    form_class = UserFullNameForm
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "email_formset" not in kwargs:
            context["email_formset"] = UserEmailFormset(instance=self.object)
        if "address_formset" not in kwargs:
            context["address_formset"] = UserAddressFormset(instance=self.object)
        return context
        
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if self.object.profile_completed:
            self.extra_context = {'title': 'profile'}
        return super().dispatch(*args, **kwargs)
        
    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.post_data,
                'files': self.request.FILES,
            })
            
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        return kwargs
           
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        self.post_data = self.request.POST.copy()
        if not self.request.POST.get("title") and self.request.POST.get("titlevalue"):
            self.post_data["title"] = self.request.POST["titlevalue"] 
        for i in range(2):
            if not self.request.POST.get("emailaddress_set-" + str(i) + "-email_type") \
                    and self.request.POST.get("emailtype" + str(i)):
                self.post_data["emailaddress_set-" + str(i) + "-email_type"] = self.request.POST["emailtype" + str(i)]
            if not self.request.POST.get("address_set-" + str(i) + "-address_type") \
                    and self.request.POST.get("addresstype" + str(i)):
                self.post_data["address_set-" + str(i) + "-address_type"] = self.request.POST["addresstype" + str(i)]
            if not self.request.POST.get("address_set-" + str(i) + "-country") \
                    and self.request.POST.get("country" + str(i)):
                self.post_data["address_set-" + str(i) + "-country"] = self.request.POST["country" + str(i)]
        form = self.get_form()
        email_formset = UserEmailFormset(self.post_data, instance=self.object)
        address_formset = UserAddressFormset(self.post_data, instance=self.object)
        
        message = "Your profile was successfully created! Let's go, Sell of buy something on Auction$!"
        if self.object.profile_completed:
            message = "Your profile was successfully updated."
        
        if form.is_valid() and email_formset.is_valid() and address_formset.is_valid():
            emails = email_formset.save()
            addresses = address_formset.save()
            messages.success(self.request, message)
            return self.form_valid(form)
            
        else:
            return self.render_to_response(self.get_context_data(
                                                        form=form,
                                                        email_formset=email_formset,
                                                        address_formset=address_formset,
                                                        err="true"
                                                        ))

    def form_valid(self, form):
        form.instance.profile_completed = True
        return super().form_valid(form)
    
        
class ActivitiesSummaryView(LoginRequiredMixin, CorrectUserTestMixin, DetailView):
    """ Display user profile details. """
    model = User
    permission_denied_message='Access to the requested page was denied.'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        
        #retrieve all listings
        #all_listings = Listing.objects.order_by("end_time")
        #
        context['user_active_listings'] = Listing.get_active().filter(
                                                    product__seller=self.request.user
                                                    ).order_by("end_time")
                                        
        # Add all bids placed by the user in a QuerySet  
        user_bids = Bid.objects.filter(
                                    bidder=self.request.user
                                ).order_by("-value") #.order_by("listing", "-value").distinct("listing")
        
        #workaround to lack of support for DISTINCT ON method in SQLite backend                        
        bidded_listings = []
        latest_bids = []
        for bid in user_bids:
            if bid.listing not in bidded_listings:
                bidded_listings.append(bid.listing)
                latest_bids.append(bid)
                                                        
        context["bids_on_active"] = [bid for bid in latest_bids if bid.listing.status == "active"]
                                                
        # Add ended listings bidded by the user in context
        context["bought"] = []
        context["sold"] = []
        ended_listings = Listing.get_ended()
        for listing in ended_listings:
            if listing.winner:
                if listing.winner == self.request.user:
                    context["bought"].append(listing)
                elif self.request.user == listing.product.seller:
                    context["sold"].append(listing)
                            
        return context
        
        
class CredentialsUpdateView(LoginRequiredMixin, CorrectUserTestMixin, UpdateView):
    """ See and update username, main email address and password."""
    model = User
    fields = ["username", "email"]
    
    def form_valid(self, form):
        messages.success(self.request, 'Your account credentials were updated.')
        return super().form_valid(form)
        
class SellActivitiesView(LoginRequiredMixin, CorrectUserTestMixin, ListView):
    """Summary of user's selling activities."""
    context_object_name = "listings_list"
    
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['pk'])
        self.queryset = Listing.objects.filter(
                                            product__seller=self.user
                                        ).order_by("end_time")
        
        return super().dispatch(*args, **kwargs)
        
    def get_context_data(self, *args, **kwargs):
        # add user's products to context
        context = super().get_context_data(*args, **kwargs)
        context["active"] =[]
        context["sold"] = []
        context["unsold"] = []
        for listing in self.queryset:
            if listing.status == "active":
                context["active"].append(listing)
            elif listing.winner:
                context["sold"].append(listing)
            elif listing.status != "not started yet":
                context["unsold"].append(listing)
        return context
        
        
class BuyActivitiesView(LoginRequiredMixin, CorrectUserTestMixin, ListView):
    """Summary of user's buying activities."""
    context_object_name = "user_bids"
    
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['pk'])
        self.queryset = Bid.objects.filter(
                                        bidder=self.user
                                    ).order_by("-value")
        
        return super().dispatch(*args, **kwargs)
        
    def get_context_data(self, *args, **kwargs):
        # add active bidded, won and lost product listings to context
        context = super().get_context_data(*args, **kwargs)
        temp = []
        context["active"] = []
        context["bought"] = []
        context["lost"] = []
        for bid in self.queryset.all():
            if bid.listing not in temp:
                temp.append(bid.listing)
                if bid.listing.status == "active":
                    context["active"].append(bid)
                elif bid.listing.winner == self.user:
                    context["bought"].append(bid)
                else:
                    context["lost"].append(bid)
        return context
        
        
class UserWatchlistView(LoginRequiredMixin, CorrectUserTestMixin, ListView):
    """Display and manage user's watchlist."""
    context_object_name = "watched_list"
    
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        user = User.objects.get(pk=kwargs['pk'])
        self.queryset = user.watchlist.all()
        
        return super().dispatch(*args, **kwargs)
    
    
class ActiveListingsView(ListView):
    """
    Displays all active listings.
    """
    queryset = Listing.get_active().order_by('-end_time')
    template_name = 'auctions/index.html'
    paginate_by = 10
    
    
class CreateListingView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    """
    Create a new listing from existing or newly added product.
    """
    model = Listing
    form_class = ListingForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = None
        listing = None
        context["from_product"] = None
        if "listing" in self.request.GET:
            try:
                listing = Listing.objects.get(pk=self.request.GET["listing"])
            except:
                listing = None
        if "product" in self.request.GET:
            try:
                product = Product.objects.filter(pk=self.request.GET["product"])
            except:
                product = None
        if listing:
            context["form"].initial = {
                "product": listing.product,
                "state": listing.state,
                "start_price": listing.start_price,
                "payment_policy": listing.payment_policy,
                "shipment_policy": listing.shipment_policy,
                "return_policy": listing.return_policy
            }
            context["from_product"] = listing.product
            user_products = Product.objects.filter(pk=listing.product.pk)
        elif product and product.first():
                user_products = product
                context["form"].fields["product"].initial = product.first()
                context["from_product"] = product.first()
        else:
            user_products = Product.objects.filter(seller=self.user)
        if not user_products.first() or "product_form" in kwargs:
            context["form"].fields["product"].disabled = True
        else:
            context["form"].fields["product"].queryset = user_products
        if "product_form" not in kwargs:
            context["product_form"] = ProductForm(initial={'seller': self.user})
        if "image_formset" not in kwargs:
            context["image_formset"] = ImageFormset()
        return context
        
        
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['pk'])
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        product_form = ProductForm(self.request.POST)
        image_formset = ImageFormset()
        
        #check if form is valid; redirect to success url
        #in case existing product is selected and correct input data for
        #other fields are provided
        if form.is_valid():
            return self.success_handler(form)
        elif not "product" in form.cleaned_data.keys() and product_form.is_valid():
            #otherwise if new product is created reinstantiate form
            product = product_form.save()
            image_formset = ImageFormset(self.request.POST, instance=product)
            if image_formset.is_valid():
                images = image_formset.save()
            form_data = {
                            "product": product,
                            "state": self.request.POST["state"],
                            "start_time": self.request.POST["start_time"],
                            "duration": self.request.POST["duration"],
                            "start_price": self.request.POST["start_price"],
                            "payment_policy": self.request.POST["payment_policy"],
                            "shipment_policy": self.request.POST["shipment_policy"],
                            "return_policy": self.request.POST["return_policy"]
                        }
            form = self.form_class(form_data)
            #redirect to success url if form is valid
            if form.is_valid():
                return self.success_handler(form)
            else:
                #delete created new product from db
                product.delete()
        return self.render_to_response(self.get_context_data(
                                                    form=form,
                                                    product_form=product_form,
                                                    image_formset=image_formset
                                                    ))
                                                        
    def success_handler(self, form):
        #redirect to success url if form is valid
        messages.success = (self.request, "Listing was successfully created.")
        return self.form_valid(form)
        
    
    def get_success_url(self):
        return reverse('auctions:update_listing', kwargs={
                                                    'user_pk':self.user.pk,
                                                    'pk':self.object.pk
                                                }
                                            )
    
    
class UpdateListingView(LoginRequiredMixin, CorrectUserTestMixin, UpdateView):
    """
    View existing listing parameters.
    Modify parameters of active but not yet started listing except product detail.
    """
    model = Listing
    form_class = ListingForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(pk=self.object.product.pk)
        return context
        
        
    def dispatch(self, *args, **kwargs):
        if 'user_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'user_pk' parameter."
            )
        elif 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['user_pk'])
        return super().dispatch(*args, **kwargs)
        
    def get_success_url(self):
        messages.success = (self.request, "Listing was successfully modified.")
        return reverse('auctions:update_listing', kwargs={
                                                    'user_pk':self.user.pk,
                                                    'pk':self.object.pk
                                                }
                                            )
                                            

@login_required
def cancel_listing(request, user_pk, listing_pk):
    """
    Helper view function fill in listing cancelled_on field on listing cancel.
    """
    req_user = get_object_or_404(User, pk=user_pk)
    if request.user != req_user:
        return redirect('auctions:index')
    listing = get_object_or_404(Listing, pk=listing_pk)
    if listing.product.seller != req_user:
        raise ValidationError
    listing.cancelled_on = timezone.now()
    listing.save()
    message_text = f"Listing for %s was cancelled" % (listing.product.name)
    messages.success = (request, message_text)
    return redirect(reverse('auctions:sell_activities', kwargs={'pk': user_pk}))
    
    
@login_required
def cancel_listings(request, user_pk):
    """
    Helper view function to cancel all active listings of user at once. Cancellation is implemented through filling of cancelled_on field of listing object.
    """
    req_user = get_object_or_404(User, pk=user_pk)
    if request.user != req_user:
        return redirect('auctions:index')
    listings = Listing.objects.filter(product__seller=req_user)
    cancelled_on = timezone.now()
    message_text = "Listings for the following products were cancelled: : "
    for listing in listings:
        listing.cancelled_on = timezone.now()
        listing.save()
        message_text = message_text + listing.product.name + ", "
    messages.success = (request, message_text)
    return redirect(reverse('auctions:sell_activities', kwargs={'pk': user_pk}))
                                            

@login_required
def mark_shipped(request, user_pk, listing_pk):
    """
    Helper view function to mark product as shipped and send respective message to a buyer.
    """
    req_user = get_object_or_404(User, pk=user_pk)
    if request.user != req_user:
        return HttpResponse("Failed")
    listing = get_object_or_404(Listing, pk=listing_pk)
    if listing.product.seller != req_user:
        raise ValidationError("You are not allowed to perform this action.")
    listing.shipment_status = 1
    listing.save()
    message_text = f"Product %s was marked as shipped and respective message was sent to the buyer." % (listing.product.name)
    messages.success = (request, message_text)
    return HttpResponse("Completed")
    
    
@login_required
def mark_paid(request, user_pk, listing_pk):
    """
    Helper view function to mark product as paid and send respective message to a buyer.
    """
    req_user = get_object_or_404(User, pk=user_pk)
    if request.user != req_user:
        return HttpResponse("Failed")
    listing = get_object_or_404(Listing, pk=listing_pk)
    if listing.winner != req_user:
        raise ValidationError("You are not allowed to perform this action.")
    listing.paid = True
    listing.save()
    message_text = f"Product %s was marked as paid and respective message was sent to the seller." % (listing.product.name)
    messages.success = (request, message_text)
    return HttpResponse("Completed")
    

@login_required
def mark_delivered(request, user_pk, listing_pk):
    """
    Helper view function to mark product as paid and send respective message to a buyer.
    """
    req_user = get_object_or_404(User, pk=user_pk)
    if request.user != req_user:
        return HttpResponse("Failed")
    listing = get_object_or_404(Listing, pk=listing_pk)
    if listing.winner != req_user:
        raise ValidationError("You are not allowed to perform this action.")
    listing.shipment_status = 2
    listing.save()
    message_text = f"Product %s was marked as delivered and respective message was sent to the seller." % (listing.product.name)
    messages.success = (request, message_text)
    return HttpResponse("Completed")
    
    
class CreateProductView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    """
    Create product to be listed.
    """
    model = Product
    form_class = ProductForm
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "image_formset" not in kwargs:
            protocol = 'http'
            current_site = get_current_site(self.request)
            domain = current_site.domain
            default_img_url = protocol + "://" + domain
            context["image_formset"] = ImageFormset(
                                                instance=self.object,
                                                initial=[
                                                    {"image_url":default_img_url+static("auctions/images/cropped-placeholder.jpg")},
                                                    {"image_url":default_img_url+static("auctions/images/cropped-placeholder.jpg")},
                                                    {"image_url":default_img_url+static("auctions/images/cropped-placeholder.jpg")}
                                                ])
        return context
        
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['pk'])
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        self.object = None
        data = {
            "seller": self.user
        }
        if request.POST["name"]:
            data["name"] = request.POST["name"]
        if request.POST["description"]:
            data["description"] = request.POST["description"]
        if request.POST["categories"]:
            data["categories"] = [Category.objects.get(pk=category) for category in request.POST["categories"]]
        form = self.form_class(data)
        image_formset = ImageFormset(request.POST)
        
        if form.is_valid():
            self.object = form.save()
            image_formset = ImageFormset(request.POST, instance=self.object)
            if image_formset.is_valid():
                images = image_formset.save()
                messages.success = (request, "New product was successfully created.")
                return redirect(reverse('auctions:update_product', kwargs={
                                                    'user_pk':self.user.pk,
                                                    'pk':self.object.pk
                                                }
                                            ))
        
        if self.object:
            self.object.delete()    
        return self.render_to_response(self.get_context_data(
                                                    form=form,
                                                    image_formset=image_formset
                                                    ))
                                            
                                            
class UpdateProductView(LoginRequiredMixin, CorrectUserTestMixin, UpdateView):
    """
    View existing product parameters.
    Modify parameters of the product that was not listed yet.
    """
    model = Product
    form_class = ProductForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ImageFormset(self.request.POST, instance=self.object)
        #if "image_formset" not in kwargs:
        else:
            context["image_formset"] = ImageFormset(instance=self.object)
        return context
        
    def dispatch(self, *args, **kwargs):
        if 'user_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'user_pk' parameter."
            )
        elif 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['user_pk'])
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        image_formset = ImageFormset(self.request.POST, instance=self.object)
        if form.is_valid() and image_formset.is_valid():
            #self.object = form.save()
            images = image_formset.save()
            return self.form_valid(form)
        else:
            return self.render_to_response(
                            self.get_context_data(
                                            form=form, image_formset=image_formset
                                        )
                        )
            
        
    def get_success_url(self):
        messages.success = (self.request, "Product was successfully modified.")
        return reverse('auctions:update_product', kwargs={
                                                    'user_pk':self.user.pk,
                                                    'pk':self.object.pk
                                                }
                                            )
                                            
                                            
@login_required
def sell_product(request, user_pk, product_pk):
    pass
    
    
#product delete function view to use with JS.
#currently use built-in DeleteView instead
#@login_required
#def delete_product(request, user_pk, product_pk):
#    """
#    Helper view function to delete not listed product..
#    """
#    req_user = get_object_or_404(User, pk=user_pk)
#    if request.user != req_user:
#        return redirect('auctions:index')
#    product = get_object_or_404(Product, pk=product_pk)
#    if product.seller != req_user:
#        raise ValidationError
#    if product.listings.first():
#        for listing in product.listings:
#            if listing.status != "not started yet":
#                messages.failure = (request, "The product can not be deleted since it is already (or was) listed")
#                raise ValidationError
                #return redirect(reverse('auctions:update_product', kwargs={"user_pk": user_pk, "pk": product_pk}))
                
#    message_text = f"Product %s was deleted" % product
#    product.delete()
#    messages.success = (request, message_text)
#    return reverse('auctions:sell_activities', kwargs={'pk': user_pk})
    
    
class DeleteProductView(LoginRequiredMixin, CorrectUserTestMixin, DeleteView):
    """
    Delete product that was not listed yet.
    """
    model = Product
    
    def dispatch(self, *args, **kwargs):
        if 'user_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'user_pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['user_pk'])
        return super().dispatch(*args, **kwargs)
    
    def get_success_url(self):
        messages.success = (self.request, "Product was deleted.")
        return reverse('auctions:sell_activities', kwargs={
                                                    'pk':self.user.pk,
                                                    }
                                            )
                                            

class ListingView(DetailView):
    model = Listing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" not in context:
            context["form"] = PlaceBidForm(initial={"value": self.object.max_bid+Decimal(1.00)})
        if "comment_form" not in context:
            context["comment_form"] = CommentForm()
        return context
        
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if self.object.product.seller == self.request.user:
            return redirect(reverse('auctions:update_listing', kwargs={'user_pk': self.request.user.pk, 'pk': self.object.pk}))
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        #self.object = self.get_object()
        data = {"listing": self.object}
        if "content" in request.POST:
            data["author"] = request.user
            data["content"] = request.POST["content"]
            comment = CommentForm(data)
            if comment.is_valid():
                new_comment = comment.save()
                messages.success = (request, "Comment was sent and published.")
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.render_to_response(self.get_context_data(comment_form=comment))
        if "value" in request.POST:
            data["bidder"] = request.user
            data["value"] = request.POST["value"]
            bid = PlaceBidForm(data)
            if bid.is_valid():
                new_bid = bid.save()
                messages.success = (request, "Bid was placed.")
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.render_to_response(self.get_context_data(form=bid))
                
    def get_success_url(self):
        return reverse('auctions:listing', kwargs={'pk':self.object.pk})
    

@login_required
def change_watchlist(request, listing_pk, action):
    """
    Helper view function to add/remove listing from user's watchlist.
    """
    try:
        listing = Listing.objects.get(pk=listing_pk)
    except:
        message.failure = (request, "The listing was not found.")
        return HttpResponse("The listing was not found.")
    if action == "add":
        request.user.watchlist.add(listing)
        messages.success = (request, "Listing was added to your watchlist")
    elif action == "remove":
        if listing in request.user.watchlist.all():
            request.user.watchlist.remove(listing)
            messages.success = (request, "Listing was removed from your watchlist.")
    return HttpResponse("Completed")
        
    
class ManageCommentsView(LoginRequiredMixin, CorrectUserTestMixin, ListView):
        
    def dispatch(self, *args, **kwargs):
        if 'user_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'user_pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['user_pk'])
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Comment.objects.filter(Q(author=self.user)|Q(listing__product__seller=self.user))


class CreateRespondToCommentView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.comment
        context["respondent"] = self.user
        return context
        
    def dispatch(self, *args, **kwargs):
        if 'user_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'user_pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['user_pk'])
        if 'comment_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'comment_pk' parameter."
            )
        self.comment = Comment.objects.get(pk=kwargs['comment_pk'])
        if self.comment.listing.product.seller != self.user:
            raise ValidationError(
                "Only the seller may answer comments left to her/his listing."
            )
        return super().dispatch(*args, **kwargs)
        
    def get_success_url(self):
        messages.success = (self.request, "Your answer was published.")
        return reverse_lazy('auctions:update_listing', kwargs={
                                                        'user_pk': self.user.pk,
                                                        'pk': self.comment.listing.pk 
                                                        })

@login_required
def bid(request, listing_pk, val):
    try:
        listing = Listing.objects.get(pk=listing_pk)
    except:
        messages.failure = (request, "The listing was not found.")
        return HttpResponse("The listing was not found.")
    
    try:    
        new_bid = Bid.objects.create(
                                bidder=request.user,
                                listing=listing,
                                value=val
                            )
    except Exception as e:
        return HttpResponse(e)
        
    messages.success = (request, "Your bid was accepted.")
    return HttpResponse("Completed")
    
    
class CreateMessageView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    model = Message
    form_class = MessageForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listing"] = self.listing
        if self.user == self.listing.product.seller:
            context["recipient"] = self.listing.winner
        else:
            context["recipient"] = self.listing.product.seller
        try:
            context["toEmail"] = context["recipient"].emailaddress_set.get(email_type='CT')
        except:
            context["toEmail"] = context["recipient"].email
        starttime = self.listing.start_time
        context["subject"] = "Auction for " + self.listing.product.name + " listed on " + starttime.strftime("%Y/%m/%d %H:%M:%S")
        if "parent" in self.request.GET:
            parent = get_object_or_404(Message, pk=self.request.GET["parent"])
            context["parent"] = parent.pk
        return context
        
    def dispatch(self, *args, **kwargs):
        if 'user_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'user_pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['user_pk'])
        if 'listing_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'listing_pk' parameter."
            )
        self.listing = Listing.objects.get(pk=kwargs['listing_pk'])
        if self.listing.product.seller != self.user and self.listing.winner != self.user:
            raise ValidationError(
                "Only the seller and the buyer in the listing may communicate regarding it."
            )
        return super().dispatch(*args, **kwargs)
        
        
class MessageView(LoginRequiredMixin, DetailView):
    model = Message
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        #validate that current user is sender or recipient of message
        if self.object.sender != request.user and self.object.recipient != request.user:
            raise ValidationError(
                "You do not have access to content of this message."
            )
        #mark message as read if user is recipient and message was not read yet 
        if not self.object.read and self.object.recipient == request.user:
            self.object.read = True
            self.object.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    

class MessengerView(LoginRequiredMixin, ListView):
    
    def get_queryset(self):
        return Message.objects.filter(Q(sender=self.request.user)|Q(recipient=self.request.user)).order_by("-time")
        

def check_unread_messages(request):
    try:
        num_unread = Message.objects.filter(recipient=request.user, read=False).count()
        return HttpResponse(json.dumps({'unread': num_unread}))
    except:
        return HttpResponse(json.dumps({'unread': 0}))


class CategoriesView(ListView):
    """
    Displays categories list.
    """
    
    def get_queryset(self):
        active_listings = Listing.get_active()
                                        
        all_categories = Category.objects.all()
        queryset1 = []
        for cat in all_categories:
            cat_prod = cat.products.all()
            active = 0
            for prod in cat_prod:
                for listing in active_listings:
                    if listing.product == prod:
                        active += 1
            queryset1.append((cat, active))
                            
        return queryset1 #.all()
    

class CategoryView(ListView):
    """
    Displays all active listings in the selected category.
    """
    
    template_name = 'auctions/index.html'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "title" not in context:
            context["title"] = "category " + self.category.name
        return context
    
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        pk = kwargs["pk"]
        self.category = get_object_or_404(Category, pk=pk)
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        product_list = self.category.products.all()
        return Listing.get_active().filter(product__in=product_list).order_by('-end_time')
                                

def search(request):
    pass
