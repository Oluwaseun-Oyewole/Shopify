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
  path("payment/<payment_option>/", views.PaymentView.as_view(), name="payment"),
  # path("add_coupon/", views.add_coupon, name="add_coupon")
  path("add_coupon/", views.AddCouponView.as_view(), name="add_coupon"),
  path("request_refund/", views.RequestRefundView.as_view(), name="request_refund"),
  path("paypal/",views.PaypalView.as_view(), name="paypal" ),
  # for shirts
  path("shirts/", views.shirts, name="shirts"),
  path("sportwear/", views.sportwear, name="sportwear"),
  path("outwear/", views.outwear, name="outwear"),
  path("search/", views.get_search_item, name="search")
  

]