from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.db.models import F, Q, Max, Case, When, Value, OuterRef, Subquery, ExpressionWrapper, DateTimeField
#from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

from .models import *
from .forms import *

#use class-based view instead
#def index(request):
#    all_listings_list = \
#            Listing.objects.order_by('-start_time').all()
#    active_listings_list = [l for l in all_listings_list if l.status == "active"]
#    context = {'active_listings_list': active_listings_list}
#    return render(request, "auctions/index.html", context)
    
class ActiveListingsView(ListView):
    queryset = Listing.objects.order_by('-start_time').all()
    template_name = 'auctions/index.html'
    paginate_by = 10

#built-in Django authentication views and customized UserCreationForm form were used
#def login_view(request):
#    if request.method == "POST":
#
        # Attempt to sign user in
#        username = request.POST["username"]
#        password = request.POST["password"]
#        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
#        if user is not None:
#            login(request, user)
#            return HttpResponseRedirect(reverse("auctions:index"))
#        else:
#            return render(request, "auctions/login.html", {
#                "message": "Invalid username and/or password."
#            })
#    else:
#        return render(request, "auctions/login.html")


#def logout_view(request):
#    logout(request)
#    return HttpResponseRedirect(reverse("auctions:index"))

class UserLoginView(LoginView):
    """ User log in interface. Redirect to the 'next' page if defined or to 
    the user's account page. """
    template_name='auctions/login.html'
    
    def get_success_url(self):
        url = self.get_redirect_url()
        return url or reverse('auctions:profile', kwargs={'pk':self.request.user.id})

def register(request):
    """ Registers a new user and creates her/his base profile. """
    if request.method == "POST":
        #username = request.POST["username"]
        #email = request.POST["email"]
        # Ensure password matches confirmation
        #password = request.POST["password"]
        #confirmation = request.POST["confirmation"]
        #if password != confirmation:
        #    return render(request, "auctions/register.html", {
        #        "message": "Passwords must match."
        #    })
        
        user_form = RegisterForm(request.POST)
        contact_form = ProfileForm(request.POST)
        
        if user_form.is_valid() and contact_form.is_valid():
            new_user = user_form.save()
            new_contact = contact_form.save(commit=False)
            new_contact.user = new_user
            new_contact.save()
            new_contact.refresh_from_db()

        # Attempt to create new user
        #try:
        #    user = User.objects.create_user(username, email, password)
            #user.save()
        #except IntegrityError:
        #    return render(request, "auctions/register.html", {
        #        "message": "Username already taken."
        #    })
            user = authenticate(request, 
                        username=user_form.cleaned_data['username'], 
                        password=user_form.cleaned_data['password1']) 
            if user is not None:
                login(request, user)
                messages.success(request, 'You were successfully registered and logged in.')
                return redirect(reverse(
                                    "auctions:profile", 
                                    kwargs={'pk':new_contact.id}
                                    )
                                )
            else:
                messages.warning(request, 'You were registered but login attempt failed.')
                return render(request, "auctions/login.html")
    else:
        user_form = RegisterForm()
        contact_form = ProfileForm()
    return render(request, "auctions/register.html", {
                                            "user_form": user_form,
                                            "contact_form": contact_form
                                            }

                    )

#
#Attempt to create class-based register view with both User and Profile creation
#forms. Unsuccessful yet. Tried two separate form as well as inline formset.
#Can't solve a problem of second form validation yet. Didn't try custom User 
#creation form with a set of fields for both models since suppose to use 
#separate forms in further update functionality. Revert back to function based
#User registration view.
#
class UserRegisterView(CreateView):
    """
    Registers a new user and creates a record of its main address for delivery
    and billing.
    """
    model = User
    form_class = RegisterForm
   
    def get_context_data(self, **kwargs):
        context = super(UserRegisterView, self).get_context_data(**kwargs)
        if "address_formset" not in kwargs:
            context["address_formset"] = UserAddressFormset()
        return context
           
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        address_formset = UserAddressFormset(self.request.POST)
        if form.is_valid() and address_formset.is_valid():
            self.object = form.save()
            addresses = address_formset.save(commit=False)
            for address in addresses:
                address.user = self.object #new_user
                address.save()
            user = authenticate(self.request, 
                                username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password1']) 
            if user is not None:
                login(self.request, user)
                messages.success(self.request, 'You were successfully registered and logged in.')
                return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(
                                                        form=form,
                                                        address_formset=address_formset
                                                        ))

    def get_success_url(self):
        return reverse_lazy("auctions:profile", kwargs={'pk':self.object.id})
    

        
#@login_required        
#def profile(request):
#    return render(request, "auctions/profile.html")

    
class ProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """ Display user profile details. """
    model = User
    template_name='auctions/profile.html'
    permission_denied_message='Access to the requested page was denied.'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        
        # Add in a QuerySet of all listings created by the user
        context['user_listings'] = Listing.objects.filter(
                                            product__seller=self.request.user
                                        )
        # Add in a QuerySet of all bids the user placed  
        context['user_bidded_listings'] = Bid.objects.values(
                                                'listing'
                                            ).filter(
                                                bidder=self.request.user
                                            ).aggregate(
                                                latest_bid=Max('value'))
                                                
        # Add in a QuerySet of all ended listings that were bidded
        context['ended_listings'] = Listing.objects.annotate(
                                            endtime=ExpressionWrapper(
                                                F('start_time')+F('duration'),
                                                output_field=DateTimeField()
                                            )).filter(
                                                (Q(
                                                endtime__lt=timezone.now()
                                                )|Q(
                                                cancelled=True)),
                                                bids__isnull=False
                                                ).order_by('-endtime')
        return context
    
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
    

@login_required    
def messenger(request):
    pass
    

def categories(request):
    pass
    

@login_required    
def create_listing(request):
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
