from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from . import views





urlpatterns = [

    #end point for the owner to edit his listing
    path("listingowner/<int:pk>", views.ownerview.as_view()),
    #end point for users to view details about listing
    path("listing/<int:pk>",views.listingdetailview.as_view()),
    #end point fro users to view all listings
    path("listing",views.listingdetailview.as_view()),
    #end point for users to place bids on a listing
    path("listing/<int:pk>/place_bid",views.place_bid),
    #end point for authenticated users to create newlisting
    path("newlisting",views.ListingCreateView.as_view()),
    #end point to view all comments on a gaven listing
    path("listing/<int:pk>/comments", views.ListingComments.as_view()),
    #end point to enable authenticated user to comment on gaven listing
    path("listing/<int:pk>/place_comment",views.placecomment.as_view()),
    #end point for admins only to view all users
    path("listusers",views.ListUsers.as_view()),
    #end point to register a new user
    path("registeruser",views.RegisterUser.as_view()),
    #--------------------------


]