from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class User(AbstractUser):
    #pass
	followers_count = models.IntegerField(default=0)
	following_count = models.IntegerField(default=0)

	def get_following_users(self):
		get_following_users = Connection.objects.filter(followed_user=self.user)
		return get_following_users

	def get_followed_users(self):
		get_followed_users = Connection.objects.filter(following_user=self.user)
		return get_followed_users

class Post(models.Model):
	post_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_author")
	likes_count = models.IntegerField()
	date = models.DateTimeField(default=datetime.now, blank=True)
	content = models.TextField()

	class Meta:
		ordering = ['-date']

class Like(models.Model):
	liked_post = models.ForeignKey(Post, on_delete=models.CASCADE)
	liking_user = models.ForeignKey(User, on_delete=models.CASCADE)
	like_is_active = models.BooleanField(default=False)

class Connection(models.Model):
	following_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_user")
	followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_user")
	connection_is_active = models.BooleanField(default=False)