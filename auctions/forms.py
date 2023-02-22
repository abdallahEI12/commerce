from django import forms
from .models import listings,bids, comments
from django.db import models
class listing_create_form(forms.ModelForm):
    class Meta:
        model = listings
        fields = ('active','title','description'
                  ,'starting_bid','image','category')
        #widgets = {
        #    "active":forms.CheckboxInput(attrs={"class":"form-control"}),
        #    "title":forms.TextInput(attrs={"class":"form-control"}),
        #    "description":forms.Textarea(attrs={"class":"form-control"}),
        #    "starting_bid":forms.NumberInput(attrs={"class":"form-control"}),
        #    "image":forms.URLInput(attrs={"class":"form-control"}),

        #           }

class ListingBidForm(forms.ModelForm):
    class Meta:
        model = bids
        fields = ('bid_value',)

class creator_listing_detail_form(forms.ModelForm):
    class Meta:
        model = listings
        fields = ('active',)

class comment_form(forms.ModelForm):
    class Meta:
        model = comments
        fields = ('comment',)
class watchlist_form(forms.Form):
    watchlist_state = forms.BooleanField()

class ListingCreateForm(forms.Form):
    active = forms.BooleanField()
    title = forms.CharField(max_length=50)
    description = forms.Textarea()
    starting_bid = forms.DecimalField(max_digits=6, decimal_places=2)
    image = forms.URLField()

