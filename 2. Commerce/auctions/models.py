from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm

class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=40)
    password = models.CharField(max_length=20)

    def __str__(self):
    	return f"{self.first_name} {self.last_name}"

class Category(models.Model):
	name = models.CharField(max_length=20)
	default_url = models.URLField()

	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'

	def __str__(self):
		return f"{self.name}"

class Listing(models.Model):
	title = models.CharField(max_length = 64)
	description = models.CharField(max_length = 300)
	starting_bid = models.IntegerField()
	current_bid = models.IntegerField()
	url = models.CharField(max_length=500,  blank=True, default="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=900&q=60")
	active = models.BooleanField(default=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category", blank=True)
	closing_date = models.DateTimeField(auto_now_add=False)
	selling_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="selling_user")

	def __str__(self):
		return f"{self.title}"

class Watchlist(models.Model):
	watching_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watching_user")
	watched_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watched_listing")

class Bid(models.Model):
	bidded_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidded_listing")
	bidding_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidding_user")
	amount = models.IntegerField()
	winning = models.BooleanField()

class Comment(models.Model):
	commenting_author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="listings")
	commented_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
	content = models.TextField(max_length=300)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['created_on']

	def __str__(self):
		return 'Comment {} by {}'.format(self.content, self.commenting_author)

class Transaction(models.Model):
	seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name="seller")
	buyer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="buyer")
	closed_listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name="closed_listing")