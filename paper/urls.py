# urls.py
from django.urls import path
from . import views

app_name = 'paper'

urlpatterns = [
    path('papers/', views.paper_list, name='paper_list'),
    path('papers/create/', views.create_paper, name='create_paper'),
    path('papers/<slug:slug>/', views.paper_detail, name='paper_detail'),
    path('papers/<slug:slug>/edit/', views.edit_paper, name='edit_paper'),
    path('papers/<slug:slug>/delete/', views.delete_paper, name='delete_paper'),
    path('papers/<slug:slug>/like', views.like_paper, name='like'),
    path('papers/<slug:slug>/dislike/', views.dislike_paper, name='dislike'),
]
