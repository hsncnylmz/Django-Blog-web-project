from django.urls import path
from . import views

urlpatterns =[
    path("", views.index, name="home"),
    path("index", views.index),
    path("blogs", views.blogs, name="blogs"),
    path('search/', views.search_results, name='search_results'),
    path("blog/<slug:slug>/", views.blog_details, name="blog_detail"),
    path("category/<slug:slug>", views.blogs_by_category, name="blogs_by_category"),
    path("blogs/<slug:slug>", views.blog_details, name="blog_details"),
    path("hashtag/<slug:slug>", views.blogs_by_tag, name="blogs_by_tag"),
    path("create/", views.create_blog, name="create_blog"),
    path('edit/<slug:slug>/', views.edit_blog, name='edit_blog'),
    path('delete/<slug:slug>/', views.delete_blog, name='delete_blog'),
    path('blogs/<slug:slug>/', views.like_blog, name='like'),
    path('blogs/<slug:slug>/dislike/', views.dislike_blog, name='dislike'),
    path('blog/<slug:slug>/reaction/', views.blog_reaction, name='blog_reaction'),
]