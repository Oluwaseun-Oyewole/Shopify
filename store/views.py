from django.shortcuts import render, get_object_or_404
from .models import *
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckOutForm


class HomeView(ListView):
  model = Item
  paginate_by = 5
  template_name = "home-page.html"

class ItemDetailView(DetailView):
  model = Item
  template_name="product-page.html"


# class OrderSummaryView(LoginRequiredMixin, View):
#   def get(self, *args,**kwargs):
#     try:
#       order = Order.objects.get(user=self.request.user, ordered=False)
#       context = {
#         "object": order,
#       }
#       return render(self.request, "order_summary.html",  context)
#     except ObjectDoesNotExist:
#       messages.error(self.request, "You do not have an active order")
#       return redirect("/")
  

@login_required
def get_order_summary(request):
  try:
    order = Order.objects.get(user = request.user, ordered=False)
    return render(request, "order_summary.html", {"object": order})
  
  except ObjectDoesNotExist:
    messages.error(request, "You do not have an active order")
    return redirect("/")


@login_required
def add_to_cart(request, slug):
  item = get_object_or_404(Item , slug=slug)
  order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
  
  order_qs = Order.objects.filter(user=request.user, ordered=False)
  
  if order_qs.exists():
      order = order_qs[0]
      
      if order.items.filter(item__slug=item.slug).exists():
        order_item.quantity +=1
        order_item.save()
        messages.info(request, "item updated")
        return redirect("order")
      else:
        messages.success(request, "This item was added to your cart")
        order.items.add(order_item)
        return redirect("order")
          
  else:
    ordered_date= timezone.now()
    order =Order.objects.create(user=request.user, ordered_date=ordered_date)
    order.items.add(order_item)  
    return redirect("order")
  
  
@login_required
def remove_from_cart(request, slug):
  item = get_object_or_404(Item, slug = slug)
  order_qs = Order.objects.filter(user=request.user, ordered=False)
  if order_qs.exists():
      order = order_qs[0]
      # check if order item is in item
      if order.items.filter(item__slug=item.slug).exists():
        order_item= OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
        order.items.remove(order_item)
        messages.info(request, "This item was removed from your cart")
        return redirect("order")
      else:
        # add a message saying the user doesn't have an order
        messages.info(request, "This item was not in your cart")
        return redirect("order")
  else:
    messages.warning(request, "You do not have an active order")
    return redirect("order")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
            else:
                order.items.remove(order_item)
                messages.info(request, "No item in the cart")
            return redirect("order")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)



class CheckoutView(View):
  def get(self, *args,**kwargs):
    form = CheckOutForm()
    return render(self.request, 'checkout-page.html', {"form": form})
  
  def post(self, *args, **kwargs):
    form = CheckOutForm(self.request.POST or None)
    if form.is_valid():
      print("This form is valid")
      form.save()
      return redirect("checkout")
    