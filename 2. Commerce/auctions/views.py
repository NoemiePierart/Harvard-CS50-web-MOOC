from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import User, Listing, Watchlist, Bid, Transaction, Comment, Category
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, "auctions/index.html")

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

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })

def create_listing(request):
    if request.method == "GET" :
        all_categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {
            'all_categories': all_categories
            })
        #return HttpResponse(type(all_categories[0]))

    if request.method == "POST" :
        input_category = request.POST["category"]
        selected_category = Category.objects.get(name=input_category)
        user_id = int(request.user.id)
        selling_user = User.objects.get(id=user_id)
        new_listing = Listing(title = request.POST["title"], 
        description = request.POST["description"], 
        starting_bid = request.POST["starting_bid"], 
        url = request.POST["url"], 
        category = selected_category,
        current_bid = request.POST["starting_bid"],
        selling_user = selling_user, 
        closing_date = request.POST["closing_date"],
        active = True)
        new_listing.save()
        message = "Your listing has been sucessfully created !"
        return render(request, "auctions/show_listing.html", {
            'listing': new_listing, 
            'message': message,
            'current_price': request.POST["starting_bid"] 

            })

def show_listing(request, listing_id):
    # Select the listing, comments, transaction, and user
    listing=Listing.objects.get(id=listing_id)
    comments = Comment.objects.filter(commented_listing = listing_id).order_by('-created_on')
    transaction = Transaction.objects.filter(closed_listing=listing)
    
    # Calculate the current price : 
    if listing.current_bid == 0 :
        listing.current_price = listing.starting_bid
    else :
        listing.current_price = listing.current_bid

    # Check the watchlist status :
    # Select the current user : 
    user_id = int(request.user.id)
    watching_user = User.objects.get(id=user_id)
    # Select the current listing : 
    watched_listing = Listing.objects.get(id=listing_id)
    # Define the wish : 
    is_watched = Watchlist.objects.filter(watching_user = watching_user, watched_listing=watched_listing).exists()

    # Delete the wish if it already exists :
    if is_watched == True:
        next_action = "delete"
    if is_watched == False:
        next_action = "add"

    if request.method == "GET" :
        return render(request, "auctions/show_listing.html", {
            "listing": listing, 
            "comments": comments, 
            "listing.current_price": listing.current_price, 
            "next_action": next_action
        })
    if request.method == "POST" :
        if request.user.id is not None :
            new_amount = int(request.POST['bid'])
            print(f"New amount : {new_amount} // Old amount : {listing.current_bid}")
            if new_amount > listing.current_price:
                # Save the new bid :
                user_id = int(request.user.id)     
                bidding_user = User.objects.get(id=user_id)
                print(f"bidding user : {bidding_user}")
                new_bid = Bid(bidded_listing=listing, bidding_user=bidding_user, amount=new_amount, winning=False)
                new_bid.save()
                # Update the current_price of the listing : 
                listing.current_bid = new_amount
                listing.save()
                # Refresh the page and confirm the new bid :
                message = "Congratulations ! Your bid has been registered !"
                return HttpResponseRedirect(reverse('show_listing', args=(listing_id,)))
            else :
                return HttpResponse("Your bid needs to be higher than the current price")        
        else : 
            return HttpResponse("Please log in before making a bid.")
     
@login_required
def comment(request):
    if request.method == "POST" :
        # Define the commenting author : 
        user_id = int(request.user.id)
        commenting_author = User.objects.get(id=user_id)
        # Define the the commented listing : 
        listing_id = request.POST["listing_id"]
        commented_listing=Listing.objects.get(id=listing_id)
        # Define the content of the comment : 
        content = request.POST['content']
        # Create the new comment and store it in the db:
        new_comment = Comment(commenting_author=commenting_author, commented_listing=commented_listing, content=content)
        new_comment.save()
        # Refresh the page and confirm the new comment :
        message = "Your comment has successfully been added !"
        return HttpResponseRedirect(reverse('show_listing', args=(listing_id,)))

@login_required
def watchlist(request):
    if request.method == "POST" :
        # Select the current user : 
        user_id = int(request.user.id)
        watching_user = User.objects.get(id=user_id)
        # Select the current listing : 
        listing_id = request.POST["listing_id"]
        watched_listing = Listing.objects.get(id=listing_id)
        # Define the wish : 
        is_watched = Watchlist.objects.filter(watching_user = watching_user, watched_listing=watched_listing).exists()

        # Delete the wish if it already exists :
        if is_watched == True:
            Watchlist.objects.filter(watching_user = watching_user, watched_listing=watched_listing).delete()
            message = "Successfully deleted listing from watchlist !"
            next_action = "add"
        else :
            wish = Watchlist(watching_user = watching_user, watched_listing=watched_listing)
            wish.save()
            message = "Successfully added listing to watchlist !"
            next_action = "delete"

        # Calculate the current price : 
        if watched_listing.current_bid == 0 :
            watched_listing.current_price = watched_listing.starting_bid
        else :
            watched_listing.current_price = watched_listing.current_bid
        
        # Render the view :     
        return render(request, "auctions/show_listing.html", {
            'message': message, 
            'listing': watched_listing, 
            'next_action': next_action, 
            'watched_listing.current_price': watched_listing.current_price
        })

    else :
        user_id = int(request.user.id)
        watching_user = User.objects.get(id=user_id)
        watchlist_list = Watchlist.objects.filter(watching_user = watching_user)
        my_list = []
        for item in watchlist_list:
            my_list.append(item.watched_listing) 
        return render(request, "auctions/watchlist.html", {
            "listings": my_list
        })

def categories(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return render(request, "auctions/categories.html", {
            'categories': categories
        })

def cat_index(request, category):
    # category_id = request.POST["category_id"]
    selected_category = Category.objects.get(name=category)
    cat_index = Listing.objects.filter(category=selected_category)
    #return HttpResponse(cat_index)
    
    return render(request, "auctions/cat_index.html", { 
        'category': selected_category,
        'cat_index': cat_index
    })

@login_required
def transaction(request):
    if request.method == "POST" :
        # Define the listing : 
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        # Define the buying_user : 
        user_id = int(request.user.id)
        buyer = User.objects.get(id=user_id)
        # Define the selling_user :
        seller = listing.selling_user
        # Save the transaction : 
        transaction = Transaction(buyer=buyer, seller=seller, closed_listing=listing)
        transaction.save()
        # Update the listing's status :
        listing.active = False
        listing.save()

        return HttpResponseRedirect(reverse('show_listing', args=(listing_id,)))
