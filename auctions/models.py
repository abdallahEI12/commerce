from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate
from django.db import models
from django.shortcuts import reverse


class User(AbstractUser):
    #each user has manytomany relation with the listings
    watch_list = models.ManyToManyField("listings",blank = True, related_name="watchers")


class categories(models.Model):
    '''all the available categories and connect them to the listings'''
    #each list has category optionally

    category = models.CharField(unique=True,blank=False,default="uncategorized",max_length=20)

    def __str__(self):
        return f"{self.category}"

class listings(models.Model):
    '''
    each listing should have active, title, description, starting bid
    ,current price, photo fields if it exists
    '''
    #each listing has manytomany relation with the categories
    active = models.BooleanField()
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    starting_bid = models.DecimalField(max_digits=6,decimal_places=2)
    current_price = models.DecimalField(max_digits=6,decimal_places=2,default=0)
    image = models.URLField(blank=True)
    #forign key to reference the person who posted the listing
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listings")
    #foreign key to reference the category
    category = models.ForeignKey(categories, on_delete=models.CASCADE,related_name="categorized")



    def __str__(self):
        return f"\ntitle = {self.title}\ndescription = {self.description}"

    def get_absolute_url(self):
        return reverse("index")

class bids(models.Model):
    #each user can place pid on listing
    #each user has manytomany relation with pids as
    #one user can place bids on multible listings
    #and one listing can has bids from multible users

    bid_value = models.DecimalField(max_digits=11,decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add = True)
    #forign key to reference the user who did the bid
    bidder  = models.ForeignKey(User,on_delete = models.CASCADE,related_name="user_bids")
    #forign key to reference the listing on which the bid is done
    listing = models.ForeignKey(listings,on_delete=models.CASCADE,related_name="bids_done")




class comments(models.Model):
    '''
    this model contains connection between comments and listings
    '''
    #each user can comment on listing

    comment_date = models.DateTimeField(auto_now = True)
    comment = models.TextField()
    #forign key to reference the user
    commenter = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_comments")
    #forign key to reference the lisiting
    listing = models.ForeignKey(listings,on_delete=models.CASCADE, related_name="listing_comments")









