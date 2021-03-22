from django.shortcuts import render
from .models import *
from django.views.generic import ListView, DetailView


class HomeView(ListView):
  model = Item
  template_name = "home-page.html"
  

class ItemDetailView(DetailView):
  model = Item
  template_name="product-page.html"

def cart(request):
  return render(request, "product-page.html", {})


def checkout(request):
  return render(request, "checkout-page.html", {})