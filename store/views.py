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
import stripe
from django.conf import settings



stripe.api_key = settings.STRIPE_SECRET_KEY


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


class CheckoutView(LoginRequiredMixin, View):
  
  def get(self, *args,**kwargs):
    form = CheckOutForm()
    order = Order.objects.get(user=self.request.user, ordered=False)
    return render(self.request, 'checkout-page.html', {"form": form, 'order':order})
  
  def post(self, *args, **kwargs):
    form = CheckOutForm(self.request.POST or None)
    # print(self.request.POST)
    try:
      order = Order.objects.get(user=self.request.user, ordered=False)
      if form.is_valid():
        # print(form.cleaned_data)
        # print("This is a valid form")
        street_address = form.cleaned_data.get('street_address')
        apartment_address = form.cleaned_data.get('apartment_address')
        country = form.cleaned_data.get('country')
        zip_code = form.cleaned_data.get('zip_code')
        # TODO: add fuunctionalities for this fields
        # same_shipping_address = form.cleaned_data.get['same_shipping_address']
        # save_info = form.cleaned_data.get['save_info']
        
        payment_option = form.cleaned_data.get('payment_option')
        billing_address = BillingAddress(
          user=self.request.user,
          apartment_address = apartment_address,
          street_address =  street_address,
        )
        billing_address.save()
        order.billing_address = billing_address
        order.save()
        # TODO: add a redrect to the selected payment option
        
        if payment_option == "S":
          return redirect("payment", payment_option="stripe")
        elif payment_option == "P":
          return redirect("payment", payment_option="paypal")
        else:
          messages.warning(self.request, "Invalid payment option selected")
          return redirect("checkout")
      
      messages.warning(self.request, 'Failed checkout')
      return redirect("checkout")
    
    except ObjectDoesNotExist:
      messages.error(request, 'You do not have any active order')
      return redirect("order")
    

class PaymentView(View):
  def get(self, *args, **kwargs):
    order= Order.objects.get(user=self.request.user, ordered=False)
    return render(self.request, 'payment.html', {'order':order})
  
  def post(self, *args, **kwargs):
    order= Order.objects.get(user=self.request.user, ordered=False)
    amount = int(order.get_total() * 100)
    token = self.request.POST.get("StripeToken")
    
    try:
      # make use of stripe Library
      charge = stripe.Charge.create( amount=amount, currency="usd", source=token)
      
    # create payment 
      payment = Payment()
      payment.stripe_charge_id = charge['id']
      payment.user  = self.request.user
      payment.amount = order.get_total() 
      payment.save()
      
      # assigning the payment to the order
      order.ordered = True
      order.payment = payment
      order.save()
      
      messages.success(self.request, "Your order was successful")
      return redirect('/')
        
    except stripe.error.CardError as e:
      body = e.json_body
      err = body.get('error', {})
      messages.warning(self.request, f"{err.get('message')}")
      return redirect("/")

    except stripe.error.RateLimitError as e:
      # Too many requests made to the API too quickly
      messages.warning(self.request, "Rate limit error")
      return redirect("/")

    except stripe.error.InvalidRequestError as e:
      # Invalid parameters were supplied to Stripe's API
      print(e)
      messages.warning(self.request, "Invalid parameters")
      return redirect("/")

    except stripe.error.AuthenticationError as e:
      # Authentication with Stripe's API failed
      # (maybe you changed API keys recently)
      messages.warning(self.request, "Not authenticated")
      return redirect("/")
              

    except stripe.error.APIConnectionError as e:
      messages.warning(self.request, "Network error")
      return redirect("/")
      # Network communication with Stripe failed

    except stripe.error.StripeError as e:
      # Display a very generic error to the user, and maybe send
      # yourself an email
      
      messages.error(self.request, "Something went wrong. You were not charged. Please try again")
      return redirect("/")
    
    except Exception as e:
      # send an email to ourselves
      messages.error(self.request, "Serious error occurred. We have been notified ")
      pass
      
    
    