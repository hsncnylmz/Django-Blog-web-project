# invoice/urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('invoice/<slug:paper_slug>/', views.invoice, name='invoice'),
    path('success/', views.success, name='success'),
    path('failure/', views.fail, name='fail'),
    # Diğer URL'ler
    path('payment/', views.payment,name='payment'),
    path('result/', views.result,name='result'),
]
