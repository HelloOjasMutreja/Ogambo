from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.userAuth, name="user-auth"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),
    path('profile/<str:username>/', views.userProfile, name="user-profile"),

    path('', views.home, name="home"),
    path('explore/', views.explore, name="explore"),
    path('bookmarks/', views.bookmarksFeed, name="bookmarks-feed"),
    path('vote/<uuid:pk>/<str:vote_type>/', views.vote, name="vote"),
    path('bookmark/<uuid:post_id>/', views.bookmark, name='bookmark'),

    path('post/<uuid:post_id>/download/', views.generateMediaDownload, name='generate_download'),

    path('post/<uuid:pk>/', views.post, name="post"),
    path('create-post/', views.createPost, name="create-post"),
    path('post/<str:pk>/edit', views.updatePost, name="update-post"),
    path('post/<str:pk>/destroy', views.deletePost, name="delete-post"),
]