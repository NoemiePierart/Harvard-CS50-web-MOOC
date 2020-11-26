from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"), 
    path("<int:listing_id>/", views.show_listing, name="show_listing"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("watchlist", views.watchlist, name="watchlist"), 
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.cat_index, name="cat_index"),
    path("comment", views.comment, name="comment"),
    path("transaction", views.transaction, name="transaction")
]
