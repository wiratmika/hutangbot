from django.conf.urls import url

from debts import views

urlpatterns = [
    url(r'^add/$', views.DebtList.as_view(), {'is_add': True})
]
