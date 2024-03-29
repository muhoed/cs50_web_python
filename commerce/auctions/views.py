from datetime import datetime
import json
import os
import re

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
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView, FormMixin
from django.views.decorators.cache import never_cache
from django.core.exceptions import ImproperlyConfigured, ValidationError, PermissionDenied
from django.template import loader
from django.core.paginator import Paginator

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
        """
        If user attempts to access other user's profile redirect her/him
        to home page and show her/him an access denied message.
        """
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
    reset workflow.
    In this school project version the view displays respective notification 
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
    """
    Sends email with reset password link to user.
    """
    
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
        #Returns the keyword arguments for instantiating the form.
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
        self.post_data = request.POST.copy()
        if not request.POST.get("title") and request.POST.get("titlevalue"):
            self.post_data["title"] = request.POST["titlevalue"] 
        for i in range(2):
            if not request.POST.get("emailaddress_set-" + str(i) + "-email_type") \
                    and request.POST.get("emailtype" + str(i)):
                self.post_data["emailaddress_set-" + str(i) + "-email_type"] = request.POST["emailtype" + str(i)]
            if not request.POST.get("address_set-" + str(i) + "-address_type") \
                    and request.POST.get("addresstype" + str(i)):
                self.post_data["address_set-" + str(i) + "-address_type"] = request.POST["addresstype" + str(i)]
            if not request.POST.get("address_set-" + str(i) + "-country") \
                    and request.POST.get("country" + str(i)):
                self.post_data["address_set-" + str(i) + "-country"] = request.POST["country" + str(i)]
        form = self.get_form()
        email_formset = UserEmailFormset(self.post_data, instance=self.object)
        address_formset = UserAddressFormset(self.post_data, instance=self.object)
        
        message = "Your profile was successfully created! Let's go, Sell of buy something on Auction$!"
        if self.object.profile_completed:
            message = "Your profile was successfully updated."
        
        if form.is_valid() and email_formset.is_valid() and address_formset.is_valid():
            emails = email_formset.save()
            addresses = address_formset.save()
            messages.success(request, message)
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
    
        
@method_decorator(never_cache, name="dispatch")
class ActivitiesSummaryView(LoginRequiredMixin, CorrectUserTestMixin, DetailView):
    """ Displays user profile details. """
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
    paginate_by = 10
    
    @method_decorator(never_cache)
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
    paginate_by = 10
    
    @method_decorator(never_cache)
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
        # add active listings bidded, won and lost by current user to context
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
    """Displays and manages user's watchlist."""
    context_object_name = "watched_list"
    paginate_by = 10
    
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        user = User.objects.get(pk=kwargs['pk'])
        self.queryset = user.watchlist.all()
        
        return super().dispatch(*args, **kwargs)
    
    
@method_decorator(never_cache, name="dispatch")
class ActiveListingsView(ListView):
    """
    Displays all active listings.
    """
    #queryset = Listing.get_active().order_by('-end_time')
    #queryset = Listing.objects.active().order_by('-end_time')
    template_name = 'auctions/index.html'
    paginate_by = 10
    
    def get_queryset(self):
        qset = Listing.objects.active().order_by('-end_time')
        return qset.all()
    
    
class CreateListingView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    """
    Creates a new listing from existing or newly added product.
    """
    model = Listing
    form_class = ListingForm
    
    def get_context_data(self, **kwargs):
        # adds product to context
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
        if not self.user.profile_completed:
            return redirect(reverse('sell_activities', kwargs={'pk':self.user.pk}))
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
        messages.success(self.request, "Listing was successfully created.")
        return self.form_valid(form)
        
    
    def get_success_url(self):
        return reverse('auctions:update_listing', kwargs={
                                                    'user_pk':self.user.pk,
                                                    'pk':self.object.pk
                                                }
                                            )
    
    
class UpdateListingView(LoginRequiredMixin, CorrectUserTestMixin, UpdateView):
    """
    Displays existing listing parameters to seller.
    Modifies parameters of active but not yet started listing except product detail.
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
        messages.success(self.request, "Listing was successfully modified.")
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
    messages.success(request, message_text)
    #return redirect(reverse('auctions:sell_activities', kwargs={'pk': user_pk}))
    return HttpResponse("Completed")
    
    
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
    messages.success(request, message_text)
    #return redirect(reverse('auctions:sell_activities', kwargs={'pk': user_pk}))
    return HttpResponse("Completed")
                                            

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
    messages.success(request, message_text)
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
    messages.success(request, message_text)
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
    messages.success(request, message_text)
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
                messages.success(request, "New product was successfully created.")
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
        messages.success(self.request, "Product was successfully modified.")
        return reverse('auctions:update_product', kwargs={
                                                    'user_pk':self.user.pk,
                                                    'pk':self.object.pk
                                                }
                                            )
    
    
class DeleteProductView(LoginRequiredMixin, CorrectUserTestMixin, DeleteView):
    """
    Deletes product that was not listed yet.
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
        messages.success(self.request, "Product was deleted.")
        return reverse('auctions:sell_activities', kwargs={
                                                    'pk':self.user.pk,
                                                    }
                                            )
                                            

class ListingView(DetailView):
    """
    Displays listing view to users over than seller.
    """
    model = Listing
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" not in context:
            context["form"] = PlaceBidForm(initial={"value": self.object.max_bid+Decimal(1.00)})
        if "comment_form" not in context:
            context["comment_form"] = CommentForm()
        return context
        
    @method_decorator(never_cache)
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
                messages.success(request, "Comment was sent and published.")
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.render_to_response(self.get_context_data(comment_form=comment))
        if "value" in request.POST:
            data["bidder"] = request.user
            data["value"] = request.POST["value"]
            bid = PlaceBidForm(data)
            if bid.is_valid():
                new_bid = bid.save()
                messages.success(request, "Bid was placed.")
                return HttpResponseRedirect(self.get_success_url())
            else:
                if float(request.POST["value"]) <= float(self.object.max_bid):
                    messages.error(request, "Your bid is less or equal to the current highest bid. Please increase a bid value and try again. Current highest bid is %s." % str(self.object.max_bid))
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
        messages.error(request, "The listing was not found.")
        return HttpResponse("The listing was not found.")
    if action == "add":
        request.user.watchlist.add(listing)
        messages.success(request, "Listing was added to your watchlist")
    elif action == "remove":
        if listing in request.user.watchlist.all():
            request.user.watchlist.remove(listing)
            messages.success(request, "Listing was removed from your watchlist.")
    return HttpResponse("Completed")
        
    
class ManageCommentsView(LoginRequiredMixin, CorrectUserTestMixin, ListView):
    """
    Displays comments to listings of current user and comments current user left on others listings.
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        context["received_comment"] = queryset["received_comment"]
        context["left_comment"] = queryset["left_comment"]
            
        return context
        
    def dispatch(self, *args, **kwargs):
        if 'user_pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'user_pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['user_pk'])
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return {
            "left_comment": Comment.objects.filter(author=self.user),
            "received_comment": Comment.objects.filter(listing__product__seller=self.user)
        }


class CreateRespondToCommentView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    """Creates answer to a comment."""
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
        messages.success(self.request, "Your answer was published.")
        return reverse_lazy('auctions:update_listing', kwargs={
                                                        'user_pk': self.user.pk,
                                                        'pk': self.comment.listing.pk 
                                                        })

@login_required
def bid(request, listing_pk, val):
    """Helper func-based view to create new bid. Invoked from JS."""
    try:
        listing = Listing.objects.get(pk=listing_pk)
    except:
        messages.error(request, "The listing was not found.")
        return HttpResponse("The listing was not found.")
    
    try:
        if not request.user.profile_completed:
            raise ValidationError("Please complete your profile before place a bid!")
        if float(listing.max_bid) == float(val):
            raise ValueError("Your bid is less or equal to the current highest bid. Please increase a bid value and try again. Current highest bid is %s€." % str(listing.max_bid))    
        new_bid = Bid.objects.create(
                                bidder=request.user,
                                listing=listing,
                                value=val
                            )
    except Exception as e:
        return HttpResponse(e)
        
    messages.success(request, "Your bid in amount of %s€ was accepted." % str(new_bid.value))
    return HttpResponse("Completed")
    
    
class CreateMessageView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    """Creates new message."""
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
        
        
@method_decorator(never_cache, name="dispatch")
class MessageView(LoginRequiredMixin, DetailView):
    """Displays message text."""
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
    

@method_decorator(never_cache, name="dispatch")
class MessengerView(LoginRequiredMixin, ListView):
    """
    Displays messages received and sent by current user.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        context["inbox"] = queryset["inbox"]
        context["outbox"] = queryset["outbox"]
            
        return context
    
    def get_queryset(self):
        return {
            "outbox": Message.objects.filter(sender=self.request.user).order_by("-time"),
            "inbox": Message.objects.filter(recipient=self.request.user).order_by("-time")
        }
        

def check_unread_messages(request):
    """
    Helper func-based view to calculate a current number of unread messages for a user.
    Invoked from JS.
    """
    try:
        if request.user.is_authenticated:
            num_unread = Message.objects.filter(recipient=request.user, read=False).count()
            return HttpResponse(num_unread)
        else:
            raise PermissionDenied
    except:
        return HttpResponse(0)


class CategoriesView(ListView):
    """
    Displays categories list.
    """
    paginate_by = 10
    
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
    
    @method_decorator(never_cache)
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
    

@method_decorator(never_cache, name="dispatch")
class SearchView(FormView):
    """
    Handles search queries. Looks in products titles and description using regular expressions.
    Returns search results as two lists. 1. Listings with occurencies in product title.
    2. Listings with occurencies in product description except listings from p.1.
    """
    form_class = SearchForm
    
    def form_valid(self, form):
        #query text can't be empty or contain only spaces
        query = form.cleaned_data["search_query"]
        if not query or re.match("^\s+$", query):
            return self.form_invalid(form)
        
        #prepare query text and active listings set
        query.lstrip().rstrip()
        pattern = "(?i)"+query
        listings = Listing.get_active()
        
        #check products titles
        self.title_matches = [listing for listing in listings if re.search(pattern, listing.product.name)]
        #check products description
        self.text_matches = []
        for listing in listings:
            if listing not in self.title_matches:
                content = listing.product.description
                queryMatch = re.search(pattern, content)
                if queryMatch:
                    self.text_matches.append([listing, "..."+content[
                    (0 if queryMatch.start()-20 < 0 else queryMatch.start()-20): \
                    queryMatch.start()], content[queryMatch.start():queryMatch.end()+1],
                    content[queryMatch.end()+1:(len(content) if queryMatch.end()+20>= \
                    len(content) else queryMatch.end()+20)]+"..."])
        if self.title_matches == [] and self.text_matches == []:
            return self.form_invalid(form)
        
        #display listings matching search criteria     
        messages.success(self.request, f"Total of {len(self.title_matches) + len(self.text_matches)} results was found")
        return render(self.request, "auctions/search.html", {
            "title": "search results",
            "in_titles": self.title_matches,
            "in_content": self.text_matches
        })
