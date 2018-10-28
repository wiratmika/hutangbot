from django.urls import path

from debts import views

urlpatterns = [
    path('', views.list),
    path('owe/', views.create_debt),
    path('pay/', views.create_payment),
    path('receive/', views.create_receivable),
    path('delete/', views.delete),
    path('outstanding/', views.calculate),
]
