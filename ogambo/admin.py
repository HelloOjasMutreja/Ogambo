from django.contrib import admin
from .models import Post, Vote, Tag

# Register your models here.

admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Vote)