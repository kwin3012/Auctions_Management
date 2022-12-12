from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Listing(models.Model):
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=255)    
    description = models.CharField(max_length=255)
    starting_price = models.IntegerField(default = 0)
    current_price = models.IntegerField(default = 0)
    user_won = models.CharField(max_length=255,default=None)

    def __str__(self):
        return f"{self.name}"

class User(AbstractUser):
    username = models.CharField(max_length = 50, blank = True, null = True, unique = True)
    email = models.EmailField(unique = True)
    phone_no = models.CharField(max_length = 10)
    def __str__(self):
        return "{}".format(self.email)
    # my_watchlist =   models.ManyToManyField(Listing, blank=True, related_name="my_watchlist")
    # my_listings = models.ManyToManyField(Listing, blank=True, related_name="my_listings")

class Bid(models.Model):
    bid = models.IntegerField(default = 0)
    bid_listing =  models.ForeignKey(Listing,default = 1, on_delete=models.CASCADE)
    bidder =  models.ForeignKey(User,default=1, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.bid}"
