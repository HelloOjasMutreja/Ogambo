from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=85, blank=True, null=True)
    avatar = models.ImageField(upload_to='profile_media/avatars/', default='default_avatar.png', blank=True, null=True)
    banner = models.ImageField(upload_to='profile_media/banners/', default='default_banner.png', blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    image = models.ImageField(upload_to='post_media/images/', null=True, blank=True)
    video = models.FileField(upload_to='post_media/videos/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title

    def upvotes(self):
        return self.votes.filter(vote_type=True).count()

    def downvotes(self):
        return self.votes.filter(vote_type=False).count()

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    vote_type = models.BooleanField()  # True for upvote, False for downvote

    def __str__(self):
        voter = self.user.username if self.user else self.ip_address
        return f"{voter} voted {'up' if self.vote_type else 'down'} on {self.post.title}"
