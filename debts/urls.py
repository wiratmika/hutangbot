from django.urls import path

from debts import views

urlpatterns = [
    path('add/', views.add_debt),
]
