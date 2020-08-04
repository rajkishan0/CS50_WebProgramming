from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Comment, Bid


def index(request):
    listings_all = Listing.objects.all()
    listings = []
    for listing in listings_all:
        if listing.active == True:
            listings.append(listing)
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """ Logs the user out and redirects them to the index page """
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


@login_required 
def create(request):
    """ Handles creating a new listing""" 
    if request.method== "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        price = request.POST["price"]
        category = request.POST["category"]
        user = User.objects.get(username=request.user.username)
        user_id = user.id

        listing = Listing(description = description, title=title, starting_bid=price, 
            image_url=image_url, user_id = user_id, category= category, current_bid = price)
        listing.save()
        return render(request, "auctions/create.html", {"message": f"Successfully listed {title}"})
    else:
        return render(request, "auctions/create.html")


def categories(request):
    """
    Handles the category page. Handles POST request of choosing a category and displays categories accordingly.
    """ 
    if request.method=="POST":
        category = request.POST["category"]
        listings_all = Listing.objects.all()
        listings = []
        for listing in listings_all:
            if listing.category.lower() == category.lower() and listing.active:
                listings.append(listing)
        return render(request, "auctions/categories.html", {"listings": listings, "category": category})
    return render(request, "auctions/categories.html", {"message": "Please enter a category"})


@login_required 
def watchlist(request, id=None):
    """ Displays watchlist of a user """ 
    user = User.objects.get(username=request.user.username)
    if id is not None:
        desired_add = Listing.objects.get(pk=id)
        user.watchlist.add(desired_add)
        user.save()

        return HttpResponseRedirect(reverse("listing_page", args=(id,)))
    listings_all = user.watchlist.all()
    listings = []
    for listing in listings_all:
        if listing.active == True:
            listings.append(listing)
    return render(request, "auctions/watchlist.html", {"listings": listings})


@login_required 
def watchlist_remove(request, id):
    """ Removes a listing from user's watchlist """
    user = User.objects.get(username=request.user.username)
    listing = Listing.objects.get(pk=id)
    user.watchlist.remove(listing)
    user.save()

    return HttpResponseRedirect(reverse("listing_page", args=(id,)))


def listing_page(request, id, message=None):
    """ 
    Displays information about a listing, determines whether or not on watchlist.
    Also handles leaving a comment (POST request) 
    """
    if 'bid_submit' in request.POST:
        # If accidently got sent here when trying to make bid POST request, send to correct view
        return bid(request, id)

    # Determine current user, None if not logging in
    listing = Listing.objects.get(pk=id)
    try:
        user = User.objects.get(username=request.user.username)
    except:
        user = None

    if request.method== "POST":
        # handle leaving a comment
        body = request.POST["body"]
        new_comment = Comment(user=user, listing=listing, body=body)
        new_comment.save()
        return HttpResponseRedirect(reverse("listing_page", args=(id,)))
    else:
        # Display the listing page and all relevant info
        # Get comments
        comments = Comment.objects.filter(listing=listing).all()

        # Get watchlist info
        if user is not None:
            user_watchlist = user.watchlist.all()
            on_watchlist = True if listing in user_watchlist else False
        else:
            on_watchlist = None

        # Get Bid info
        try:
            current_bid = Bid.objects.filter(listing=listing).order_by('-id')[0]
            number_bids = len(Bid.objects.filter(listing=listing).all())
        except:
            # No bids made yet for this listing, populate for template
            current_bid = Bid(user=User.objects.get(pk=listing.user_id), bid = listing.starting_bid, listing=listing)
            number_bids = 0

        # Get started by username
        username = User.objects.get(pk=listing.user_id).username

        # Determine whether or not user started the auction
        if user is not None: 
            started_listing = True if user.username == username else False
        else:
            started_listing = False

        # Check if the auction is open
        active = listing.active

        return render(request, "auctions/listing_page.html", 
            {"listing": listing, "on_watchlist": on_watchlist, "comments": comments, 
            "username": username, "current_bid": current_bid, "number_bids": number_bids, "message": message,
            "started_listing": started_listing, "active": active})


def bid(request, id):
    """
    Handles the post request for bid being placed on a listing page
    """
    if request.method == "POST":
        bid = request.POST["bid"]
        listing = Listing.objects.get(pk=id)
        try:
            current_bid = Bid.objects.filter(listing=listing).order_by('-id')[0].bid
        except:
            current_bid = 0

        if int(bid) <= int(listing.starting_bid) or int(bid) <= int(current_bid):
            # Error page
            request.method = "GET"
            return listing_page(request, id, "Bid must be greater than starting bid AND current bid!")
        else:
            # Create a new bid for this listing
            new_bid = Bid(user = User.objects.get(pk=request.user.id), listing=listing, bid=bid)
            new_bid.save()
            listing.current_bid = new_bid.bid
            listing.save()
            return HttpResponseRedirect(reverse("listing_page", args=(id,)))

    else:
        # Should not have been to get here, some kind of error
        return render(request, "auctions/error.html")

def close(request, id):
    listing = Listing.objects.get(pk=id)
    user = User.objects.get(username=request.user.username)
    if user.id != listing.user_id:
        # Accessed this page without being the user that stared the auction with id ID
        return render(request, "auctions/error.html")
    try:
        current_bidder_id = Bid.objects.filter(listing=listing).order_by('-id')[0].user.id
    except:
        # No bids made yet for this listing, populate for template
        current_bidder_id = -1
    listing.winner_id = current_bidder_id
    listing.active = False
    listing.save()
    return HttpResponseRedirect(reverse("listing_page", args=(id,)))

