from django.contrib import admin
from .models import Post, Vote, Tag, Profile

# Register your models here.

admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Vote)
admin.site.register(Profile)