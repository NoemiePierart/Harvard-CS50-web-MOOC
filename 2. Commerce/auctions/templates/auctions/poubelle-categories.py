        
        # Update the confirmation message
        message = "Your comment has successfully been added !"
        # Render the show page : 
        comments = Comment.objects.filter(commented_listing=commented_listing)
        return render(request, "auctions/show_listing.html", {
            "listing": listing, 
            "comments": comments
        })