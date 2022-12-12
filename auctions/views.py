from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.db import IntegrityError
from .models import User, Bid, Listing
from django.contrib.auth.decorators import login_required
from django import forms


def index(request):
    listings = Listing.objects.filter(isActive = True)
    current_user = request.user  
    data = {"listings": listings,}
    return render(request, "auctions/index.html", data)

def login_view(request):
    if request.method != "POST":
        return render(request, "auctions/login.html")

    # Attempt to sign user in
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

        # Check if authentication successful
    if user is None:
        return render(request, "auctions/login.html", {
            "message": "Invalid username and/or password."
        })
    login(request, user)
    return HttpResponseRedirect(reverse("index"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method != "POST":
        return render(request, "auctions/register.html")
        
    username = request.POST["username"]
    email = request.POST["email"]

    # Ensure password matches confirmation
    password = request.POST["password"]
    confirmation = request.POST["confirmation"]
    if password != confirmation:
        return render(request, "auctions/register.html", {
            "message": "Passwords must match."
        })

    # Attempt to create new user
    try:
        user = User.objects.create_user(username, email, password)
        user.save()
    except IntegrityError:
        return render(request, "auctions/register.html", {
            "message": "Username already taken."
        })
    login(request, user)
    return HttpResponseRedirect(reverse("index"))

class ListingForm(forms.ModelForm):
    description = forms.CharField( label='')
    name = forms.CharField( label='')
    starting_price = forms.IntegerField(label='')
    class Meta:
        model = Listing
        fields= ['description', 'name', 'starting_price']
        widgets = {
            'description':forms.TextInput(attrs={'class': 'form-description'}),
            'name': forms.TextInput(attrs={'class': 'form-name'}),
            'starting_price': forms.NumberInput(attrs={'class': 'form-starting_price'})
        }

@login_required(login_url='login')
def create(request):
    current_user = request.user

    if request.method == "POST":
        listingform = ListingForm(request.POST)
        if listingform.is_valid():
            added_listing = listingform.save(commit= False)
            added_listing.isActive = True
            added_listing.current_price =  added_listing.starting_price
            added_listing.save()
            current_user.my_listings.add(added_listing)
            return redirect("/"+str(added_listing.id))
        else:
            data ={
                "listingform": listingform,
            }
            return render(request, "auctions/create.html", 
                data
            )
    else:
        data ={
            "listingform": ListingForm(),
        }
        return render(request, "auctions/create.html", 
            data
        )
