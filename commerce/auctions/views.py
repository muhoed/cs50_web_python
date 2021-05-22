from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
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


def register(request):
    
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
        contact_form = ContactForm(request.POST)
        
        if user_form.is_valid() and contact_form.is_valid():
            new_user = user_form.save()
            new_contact = contact_form.save(commit=False)
            new_contact.user = new_user
            new_contact.save()

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
            if new_user is not None:
                login(request, new_user)
                return HttpResponseRedirect(reverse("auctions:index"), {
                            "message":"You were successfully registered and logged in"})
            else:
                return render(request, "auctions/index.html",
                                {'message':'You were registered but login attempt failed.'})
    else:
        user_form = RegisterForm()
        contact_form = ContactForm()
    return render(request, "auctions/register.html", {
                                            "user_form": user_form,
                                            "contact_form": contact_form
                                            }
                    )


        
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
    
@login_required
def bid(request):
    pass
    

def search(request):
    pass
