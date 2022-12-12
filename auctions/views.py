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
        return render(request, "auctions/login.html", {"message": "Invalid username and/or password."})
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
        return render(request, "auctions/register.html", {"message": "Username already taken."})
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

@login_required
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
            return redirect("index")
        else:
            data = {"listingform": listingform,}
            return render(request, "auctions/create.html", data)
    else:
        data = {"listingform": ListingForm(),}
        return render(request, "auctions/create.html",  data)

class BidForm(forms.ModelForm):
    bid = forms.IntegerField(label='',
    required=False,
    widget=forms.TextInput(attrs={ 'required': 'false' }))
    class Meta:
        model = Bid
        fields = ['bid']

def listing_profile(request, product_id):
    product =  Listing.objects.get(id = product_id)
    current_user = request.user
    _isActive = product.isActive
    data = {     
        "WinnerName": current_user,
        "isActive": _isActive,
        "bid_isvalid" : True,
        "has_content": True,
        "product": product,
        "bidform": BidForm(initial={'bid': product.current_price}),
    }

    if current_user.is_authenticated:
        isMine = product in current_user.my_listings.all()

        args = Bid.objects.filter(bid_listing=product)
        if args.count() >= 1:
            highest_bid = args.order_by('-bid')[0]
            isWinner = highest_bid.bidder == current_user
            data["isWinner"] = isWinner

        data["isMine"] = isMine

    return render(request, "auctions/profile.html", data)

@login_required
def place_bid(request, product_id):
    product =  Listing.objects.get(id = product_id)
    current_user = request.user

    if request.method == "POST":
        bidform = BidForm(request.POST or None)
        if bidform.is_valid() and bidform != None:
            added_bid  = bidform.save(commit=False)
            if (added_bid.bid < product.starting_price or added_bid.bid <= product.current_price):
                return render(request, "auctions/profile.html",{
                    "WinnerName": current_user,
                    "isActive": True,
                    "bid_isvalid" : False,
                    "has_content": True,
                    "product": product,
                    "bidform": BidForm(),
                }) 

            added_bid.bid_listing = product
            added_bid.bidder = current_user
            added_bid.save()
            product.current_price = added_bid.bid
            product.user_won = current_user.username
            product.save()
            return redirect("index")

    return redirect('/' + str(product_id))

@login_required()
def close(request):
    if request.method == "POST":
        form = request.POST.get("product_id")
        product =  Listing.objects.get(id = form)
        product.isActive = False
        product.save()
    return redirect('/' + str(form))

