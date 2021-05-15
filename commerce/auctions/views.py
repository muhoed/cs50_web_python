from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from .forms import *


def index(request):
    all_listings_list = \
            Listing.objects.order_by('-start_time').all()
    active_listings_list = [l for l in all_listings_list if l.status == "active"]
    #categories_list = Category.objects.all()
    context = {'active_listings_list': active_listings_list} #,
    #            'categories_list': categories_list}
    return render(request, "auctions/index.html", context)

#used standard Django authentication views and register form instead
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


def register(request):
    regform_set = inlineformset_factory(
                    Address, User, fk_name="sender", fields="__all__")
    if request.method == "POST":
        #username = request.POST["username"]
        #email = request.POST["email"]
        form = regform_set(request.POST)

        # Ensure password matches confirmation
        #password = request.POST["password"]
        #confirmation = request.POST["confirmation"]
        #if password != confirmation:
        #    return render(request, "auctions/register.html", {
        #        "message": "Passwords must match."
        #    })
        if form.is_valid():
            form.save()

        # Attempt to create new user
        #try:
        #    user = User.objects.create_user(username, email, password)
            #user.save()
        #except IntegrityError:
        #    return render(request, "auctions/register.html", {
        #        "message": "Username already taken."
        #    })
            login(request, get_object_or_404(User, username=form.username))
            return HttpResponseRedirect(reverse("auctions:index"), {
                        "message":"You were successfully registered and logged in"})
	#else:
    form = regform_set()
    return render(request, "auctions/register.html", {"form": form})


        
@login_required        
def profile(request):
    return render(request, "auctions/profile.html")
    

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
    

def search(request):
    pass
