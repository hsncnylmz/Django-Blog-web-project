from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login_request, name="login"),
    path("register", views.register_request, name="register"),
    path("logout", views.logout_request, name="logout"),
    path('profile/<slug:slug>/', views.profile, name='profile'),
    path('profile/edit/<slug:slug>/', views.edit_profile, name='edit_profile'),
]