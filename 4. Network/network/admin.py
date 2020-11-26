from django.contrib import admin
from .models import User, Post, Connection, Like

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Connection)
admin.site.register(Like)