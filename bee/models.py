from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    encrypted_password = models.CharField(max_length=128)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Generate a random salt for password hashing
        salt = get_random_string()
        # Hash the user's password using the salt
        self.encrypted_password = make_password(self.user.password, salt=salt)
        super().save(*args, **kwargs)

class WatchList(models.Model):
    anime_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('anime_id', 'user',)

    def __str__(self):
        return f'{self.user.username} - {self.anime_id}'


class ReadList(models.Model):
    manga_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('manga_id', 'user',)

    def __str__(self):
        return f'{self.user.username} - {self.manga_id}'


class Reaction_anime(models.Model):
    LIKE = 0
    DISLIKE = 1
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    anime_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.PositiveSmallIntegerField(choices=REACTION_CHOICES, default=LIKE)
    class Meta:
        unique_together = ('anime_id', 'user','reaction_type',)
    def __str__(self):
        return f'{self.user.username} {self.reaction_type} (0->likes, 1->dislikes)'
    
class Reaction_manga(models.Model):
    LIKE = 0
    DISLIKE = 1
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    manga_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.PositiveSmallIntegerField(choices=REACTION_CHOICES, default=LIKE)
    def __str__(self):
        return f'{self.user.username} {self.reaction_type} (0->likes, 1->dislikes)'

class Comment_anime(models.Model):
    anime_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
    def __str__(self):
        return f'{self.user.username} commented {self.content}'
    
class Comment_manga(models.Model):
    manga_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
    def __str__(self):
        return f'{self.user.username} commented {self.content}'