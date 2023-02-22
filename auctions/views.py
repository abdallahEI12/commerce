import decimal

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormMixin
from django.views.generic.list import ListView

from .forms import ListingCreateForm,listing_create_form, ListingBidForm, creator_listing_detail_form, comment_form, watchlist_form
from .models import *


class index(ListView):
    template_name = "auctions/index.html"
    queryset = listings.objects.filter(active=True)
    context_object_name = "active_listings"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(index, self).get_context_data(**kwargs)
        context["categories"] = categories.objects.all()
        return context


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if "next" in request.POST:
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
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
    else:
        return render(request, "auctions/register.html")


# ============================================================ #

class Newlisting(LoginRequiredMixin, CreateView):
    model = listings
    template_name = "auctions/create_listing.html"
    form_class = listing_create_form

    # you can provide a url with the success_url attribute
    # at which the user will be redirected to if the if listing
    # was created successfully but i have provided a url at the model

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.current_price = 0
        return super().form_valid(form)


class listing_detail(LoginRequiredMixin, DetailView, FormMixin):
    login_url = "login"
    redirect_field_name = "next"
    model = listings
    template_name = "auctions/listing_detail.html"

    def get_success_url(self):
        return reverse("listing_detail", kwargs={"pk": self.object.id})

    def get_form_class(self, form_class=None):
        if self.request.user == self.object.created_by:
            return creator_listing_detail_form
        else:
            return ListingBidForm

    def get_initial(self):
        if self.request.user == self.object.created_by:
            return {"active": self.object.active}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if "submit-comment" in request.POST:
            comment = comments.objects.create(commenter=self.request.user,
                                              comment=request.POST.get("comment"),
                                              listing=self.object)
            comment.save()
            return HttpResponseRedirect(reverse("listing_detail", kwargs={"pk": self.object.id}))
        elif "change-state" in request.POST:
            if request.POST.get("change-state") == "remove":
                User.objects.get(id = self.request.user.id).watch_list.remove(self.object)
            else:
                User.objects.get(id=self.request.user.id).watch_list.add(self.object)

            return HttpResponseRedirect(reverse("listing_detail", kwargs={"pk": self.object.id}))
        else:
            if form.is_valid() and self.request.user != self.object.created_by:

                if form.instance.bid_value > self.listing_max_bid() and form.instance.bid_value > self.object.starting_bid:
                    listing = listings.objects.get(id=self.object.id)
                    listing.current_price = float(form.instance.bid_value)
                    listing.save()
                    return self.form_valid(form)
                else:
                    return self.form_invalid(form)
            elif form.is_valid() and self.request.user != self.object.created_by:
                return self.form_valid(form)
            else:
                return self.form_valid(form)
    def get_context_data(self, **kwargs):
        context = super(listing_detail, self).get_context_data(**kwargs)
        if not self.object.active and self.request.user != self.object.created_by and self.user_max_bid() == self.listing_max_bid():
            context["win_message"] = "congrats you won!"
        context["comment_form"] = comment_form()
        context["comments"] = comments.objects.filter(listing=self.object)
        context["bids_count"] = len(bids.objects.filter(listing=self.object))
        context["is_watchlisted"] = self.is_watchlisted()
        context['watchlist_form'] = watchlist_form({"watchlist_state": self.is_watchlisted()})
        return context

    def form_valid(self, form):
        if self.request.user == self.object.created_by:
            listing = listings.objects.get(pk=self.object.id)
            if self.request.POST.get("active"):
                listing.active = True
            else:
                listing.active = False
            listing.save()
        else:
            bid = bids.objects.create(
                bid_value=form.instance.bid_value,
                bidder=self.request.user,
                listing=self.get_object()
            )
            bid.save()
        return super().form_valid(form)

    def user_max_bid(self):
        # return the user's max bid on the listing
        if bids.objects.filter(listing=self.object, bidder=self.request.user).aggregate(Max("bid_value"))[
            "bid_value__max"] is None:
            return 0
        else:
            return bids.objects.filter(listing=self.object, bidder=self.request.user).aggregate(Max("bid_value"))[
            "bid_value__max"]

    def listing_max_bid(self):
        # return highest bid placed on the listing

        if bids.objects.filter(listing=self.object).aggregate(Max("bid_value"))["bid_value__max"]is None:
            return 0
        else:
            return bids.objects.filter(listing=self.object).aggregate(Max("bid_value"))["bid_value__max"]

    def form_invalid(self, form):
        try :
            decimal.Decimal(form.instance.bid_value)
            if form.instance.bid_value < self.listing_max_bid() or form.instance.bid_value < self.object.starting_bid:
                context = self.get_context_data()
                context['bid_error_message'] = "your bid must be higher than biggest bid and starting bid"
                return render(self.request, self.template_name, context)
            else:
                return super().form_invalid(form)
        except:
            return super().form_invalid(form)

    def is_watchlisted(self):
        if self.request.user in self.object.watchers.all():
            return True
        else:
            return False


class watchlist(ListView):
    template_name = "auctions/watchlist.html"
    context_object_name = "user_watchlist"

    def get_queryset(self):
        return User.objects.get(username=self.request.user).watch_list.all()



class category_listings(ListView):
    template_name = "auctions/category_listings.html"
    context_object_name = "listings"


    def get_queryset(self):
        return listings.objects.filter(category = self.kwargs["pk"])
