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
    ANIME = 'anime'
    anime_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.PositiveSmallIntegerField(choices=REACTION_CHOICES)
    def __str__(self):
        return f'{self.user.username} {self.reaction_type}s'
    
class Reaction_manga(models.Model):
    LIKE = 0
    DISLIKE = 1
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    MANGA = 'manga'
    manga_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.PositiveSmallIntegerField(choices=REACTION_CHOICES)
    def __str__(self):
        return f'{self.user.username} {self.reaction_type}s'

class Comment_anime(models.Model):
    ANIME = 'anime'
    anime_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # for reply to a comment
    parent = models.ForeignKey('self' , null=True , blank=True , on_delete=models.CASCADE , related_name='replies')
    class Meta:
        ordering=['-created_at']
    def __str__(self):
        return f'{self.user.username} commented {self.content} on {self.type}: {self.id}'
    @property
    def children(self):
        return Comment_anime.objects.filter(parent=self).reverse()
    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False
    
class Comment_manga(models.Model):
    MANGA = 'manga'
    manga_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # for reply to a comment
    parent = models.ForeignKey('self' , null=True , blank=True , on_delete=models.CASCADE , related_name='replies')
    class Meta:
        ordering=['-created_at']
    def __str__(self):
        return f'{self.user.username} commented {self.content} on {self.type}: {self.id}'
    @property
    def children(self):
        return Comment_manga.objects.filter(parent=self).reverse()
    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False