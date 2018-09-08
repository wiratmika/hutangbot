from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.create, { 'is_add': True })
]
