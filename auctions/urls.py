from django.urls import path

from . import views

urlpatterns = [
    path("", views.index.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing",views.Newlisting.as_view(),name = "create_listing"),
    path("listing_detail/<int:pk>/", views.listing_detail.as_view(),name = "listing_detail"),
    path("wathclist",views.watchlist.as_view(), name= "watchlist"),
    path("categories/<int:pk>",views.category_listings.as_view(),name="category_listings"),
    path("togglewatchlisting/<int:listing_id>",views.togglewatchlist.as_view(),name="togglewatchlist"),
    path("categories",views.all_categories.as_view(),name="categories")
]
