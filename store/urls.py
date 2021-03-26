from django.urls import path
from . import  views


urlpatterns = [
  path("", views.HomeView.as_view(), name="home"),
  path("product/<slug:slug>/", views.ItemDetailView.as_view(), name="product"),
  path("add_to_cart/<slug>/",  views.add_to_cart, name="add_to_cart"),
  path("remove_from_cart/<slug>/",  views.remove_from_cart, name="remove_from_cart"),
  path("checkout/", views.CheckoutView.as_view(), name="checkout"),

  # path("order_summary/", views.OrderSummaryView.as_view(), name="order_summary"),
  path("order/", views.get_order_summary, name="order"),
  path("remove_single_item_from_cart/<slug>/",  views.remove_single_item_from_cart, name="remove_single_item_from_cart"),

]