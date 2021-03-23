from django.urls import path
from . import  views

urlpatterns = [
  path("", views.HomeView.as_view(), name="home"),
  path("product/<slug:slug>/", views.ItemDetailView.as_view(), name="product"),
  path("add_to_cart/<slug>/",  views.add_to_cart, name="add_to_cart"),
  path("remove_from_cart/<slug>/",  views.remove_from_cart, name="remove_from_cart"),
  path("checkout/", views.checkout, name="checkout")
]