
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"), 
    path("<int:user_id>/", views.show_user, name="show_user"),
    path("<int:user_id>/follow", views.follow, name="follow"), 
    path("<int:user_id>/following", views.following, name="following"),
    path("posts/<int:post_id>/edit", views.edit, name="edit"),
    path("posts/<int:post_id>/like", views.like, name="like")
]
