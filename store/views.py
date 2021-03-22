from django.shortcuts import render
from .models import *


def item_list(request):
  context = {
    "items":  Item.objects.all()
  }
  return render(request, "home-page.html", {"items":Item.objects.all()})

def cart(request):
  return render(request, "product-page.html", {})


def checkout(request):
  return render(request, "checkout-page.html", {})