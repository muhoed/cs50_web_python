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
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.db.models import (F, Q, Max, Case, When, Value, OuterRef, 
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
from django.views.generic.edit import CreateView, UpdateView
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
        return (get_object_or_404(User, pk=self.kwargs['pk']) == self.request.user)
        
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
        #return super().form_valid(form)
    
    
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
        
        #retrieve all listings to cache
        all_listings = Listing.objects.all().order_by("end_time")
        
        # Add all active listings created by the user in a QuerySet
        context['user_active_listings'] = all_listings.filter(
                                            product__seller=self.request.user, cancelled_on__isnull=True).annotate(endtime=ExpressionWrapper(F("start_time") + F("duration"), output_field=DateTimeField()).filter(endtime__gt=timezone.now())
                                        )
                                        
        # Add all bids placed by the user in a QuerySet  
        bidded_listings = Bid.objects.values(
                                                'listing'
                                            ).filter(
                                                bidder=self.request.user
                                            ).aggregate(
                                                latest_bid=Max('value'))
                                                context["user_bidded_listings"] = bidded_listings.annotate(endtime=ExpressionWrapper(F("start_time") + F("duration"), output_field=DateTimeField()).filter(endtime__gt=timezone.now(), cancelled_on__isnull=True)
                                        )
                                                
        # Add ended listings bidded by the user in context
        context["bought"] = []
        context["sold"] = []
        for listing in all_listings:
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
        self.queryset = Listing.objects.filter(product__seller=self.user)
        
        return super().dispatch(*args, **kwargs)
        
    def get_context_data(self, *args, **kwargs):
        # add user's products to context
        context = super().get_context_data(*args, **kwargs)
        context["products_list"] = []
        context["active"] =[]
        context["sold"] = []
        context["unsold"] = []
        for listing in self.queryset:
            if listing.product not in context["products_list"]:
                context["products_list"].append(listing.product)
            if listing.status == "active":
                context["active"].append(listing)
            elif listing.winner:
                context["sold"].append(listinh)
            elif listing.status != "not started yet":
                context["unsold"].append(listing)
        return context
        
        
class BuyActivitiesView(LoginRequiredMixin, CorrectUserTestMixin, ListView):
    """Summary of user's buying activities."""
    context_object_name = "user_bidded_listings"
    
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['pk'])
        self.queryset = Bid.objects.values('listing').filter(
                                                bidder=self.request.user
                                            ).aggregate(latest_bid=Max('value'))
        
        return super().dispatch(*args, **kwargs)
        
        
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
    queryset = Listing.objects.order_by('-start_time').all()
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
        #product_form.fields["seller"] = self.user
        image_formset = ImageFormset()
        
        if not hasattr(form.fields, "product") and product_form.is_valid():
            product = product_form.save()
            image_formset = ImageFormset(self.request.POST, instance=product)
            form.fields["product"].initial = product.id
            if image_formset.is_valid():
                images = image_formset.save()
            
        message = "Listing was successfully created."
        
        if form.is_valid():
            messages.success(self.request, message)
            return self.form_valid(form)
            
        else:
            return self.render_to_response(self.get_context_data(
                                                        form=form,
                                                        product_form=product_form,
                                                        image_formset=image_formset
                                                        ))
                                                        
    def get_success_url(self):
        return reverse(
                    'auctions:update_listing',
                    kwargs={
                        'pk': self.user.pk,
                        'listing_pk': self.object.pk
                        }
                    )
    
    
class UpdateListingView(LoginRequiredMixin, CorrectUserTestMixin, UpdateView):
    """
    Update existing listing for on-the-fly modifications and relisting.
    """
    model = Listing
    form_class = ListingForm
    
    
class ProductView(LoginRequiredMixin, CorrectUserTestMixin, CreateView):
    """
    Create product to be listed.
    """
    model = Product
    form_class = ProductForm
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "image_formset" not in kwargs:
            context["image_formset"] = ImageFormset(instance=self.object)
        return context
        
    def dispatch(self, *args, **kwargs):
        if 'pk' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'pk' parameter."
            )
        self.user = User.objects.get(pk=kwargs['pk'])
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.seller = self.user
        image_formset = ImageFormset(self.post_data, instance=self.object)
        
        message = "New product was successfully created."
        
        if form.is_valid() and image_formset.is_valid():
            images = image_formset.save()
            messages.success(self.request, message)
            return self.form_valid(form)
            
        else:
            return self.render_to_response(self.get_context_data(
                                                        form=form,
                                                        image_formset=image_formset
                                                        ))
    
    
@login_required    
def messenger(request):
    pass
    

def categories(request):
    pass
    
    
def listing(request, listing_id):
    pass
    

@login_required
def watchlist(request):
    pass
    
@login_required
def bid(request):
    pass
    

def search(request):
    pass
