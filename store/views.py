from django.shortcuts import render, get_object_or_404
from .models import *
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckOutForm, CouponForm, RefundForm
import stripe
from django.conf import settings
import random
import string
from decimal import Decimal

def create_ref_code():
  return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


stripe.api_key = settings.STRIPE_SECRET_KEY


class HomeView(ListView):
  model = Item
  paginate_by = 8
  template_name = "home-page.html"

class ItemDetailView(DetailView):
  model = Item
  template_name="product-page.html"
  

def shirts(request):
  items = Item.objects.filter(category = 'S' )
  return render(request, 'shirt_page.html', {'items':items})

def sportwear(request):
  items = Item.objects.filter(category = 'SW' )
  return render(request, 'sportwear_page.html', {'items':items})

def outwear(request):
  items = Item.objects.filter(category="OW")
  return render(request, 'outwear.html', {"items": items})

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
    messages.warning(request, "You do not have an active order")
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


def get_search_item(request):  
  if  request.method == 'GET':
    search_item = request.GET.get('search')
    items = Item.objects.filter(title=search_item)
    try:
      if items.exists():
        items = Item.objects.filter(title=search_item)
        return render(request,"search.html",{"items":items})  
      else:
        messages.warning(request, 'No such  Item')
        return redirect("/")
    except ObjectDoesNotExist:
      print("nothing dey here")
  return redirect("/")
  

# for empty strings
def is_valid_form(values):
  valid =True
  for field in values:
    if field == "":
      valid=False
  return valid   

class CheckoutView(LoginRequiredMixin, View):
  
  def get(self, *args,**kwargs):
    try:
      form = CheckOutForm()
      order = Order.objects.get(user=self.request.user, ordered=False)
      couponform=CouponForm()
      context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
    
      shipping_address_qs = Address.objects.filter(user=self.request.user,  address_type="S", default = True)
      
      if shipping_address_qs.exists():
        context.update({'default_shipping_address':shipping_address_qs[0]})
        
        
      billing_address_qs = Address.objects.filter(user=self.request.user,  address_type="B", default = True)
      
      if billing_address_qs.exists():
        context.update({'default_billing_address':billing_address_qs[0]})
  
      return render(self.request, 'checkout-page.html', context)
      
    except ObjectDoesNotExist:
      messages.warning(self.request, 'You d not have any active order')
      return redirect("checkout")
  
  def post(self, *args, **kwargs):
    form = CheckOutForm(self.request.POST or None)
    try:
      order = Order.objects.get(user=self.request.user, ordered=False)
      if form.is_valid():
        # print(form.cleaned_data)
        # print("This is a valid form")
        
        # to check if we are using the default shipping address
        
        use_default_shipping = form.cleaned_data.get("use_default_shipping")
        if use_default_shipping:
          print ("Using the dafault shipping address")
          address_qs = Address.objects.filter(user=self.request.user, default=True, address_type="S")
          if address_qs.exists():
            shipping_address =  address_qs[0]
            order.shipping_address = shipping_address
            order.save()
            
          else:
            messages.info(self.request, 'No default shipping address available')
            return redirect("checkout")
        else:
          print("User entering a new shipping address")
          shipping_address1 = form.cleaned_data.get('shipping_address')
          shipping_address2 = form.cleaned_data.get('shipping_address2')
          shipping_country = form.cleaned_data.get('shipping_country')
          shipping_zip = form.cleaned_data.get('shipping_zip')
          
          if is_valid_form([shipping_address1, shipping_address2, shipping_country, shipping_zip]):
          # payment_option = form.cleaned_data.get('payment_option')
            shipping_address = Address(
              user=self.request.user,
              apartment_address = shipping_address2,
              street_address =  shipping_address1,
              zip_code = shipping_zip,
              country = shipping_country,
              address_type="S" 
            )
            shipping_address.save()
            order.shipping_address = shipping_address
            order.save()
        
            set_default_shipping = form.cleaned_data.get("set_default_shipping")
        
            if set_default_shipping:
              shipping_address.default = True
              shipping_address.save()
              
          else:
            messages.info(self.request, 'Please fill in the required  shipping  address fields')
            return redirect("checkout")
        
        use_default_billing = form.cleaned_data.get("use_default_billing")
        same_billing_address =form.cleaned_data.get("same_billing_address")
        
        if same_billing_address:
          billing_address = shipping_address
          # clone the billing address
          billing_address.pk = None
          # end of clone 
          billing_address.save()
          billing_address.address_type="B"
          billing_address.save()
          
        elif use_default_billing:
          print ("Using the dafault billing address")
          address_qs = Address.objects.filter(user=self.request.user, default=True, address_type="B")
          if address_qs.exists():
            billing_address =  address_qs[0]
            order.billing_address = billing_address
            order.save()
          else:
            messages.info(self.request, 'No default billing address available')
            return redirect("checkout")
        else:
          print("User entering a new billing address")
          billing_address1 = form.cleaned_data.get('billing_address')
          billing_address2 = form.cleaned_data.get('billing_address2')
          billing_country = form.cleaned_data.get('billing_country')
          shipping_zip = form.cleaned_data.get('billing_zip')
          
          if is_valid_form([billing_address1, billing_address2, billing_country, shipping_zip]):
          # payment_option = form.cleaned_data.get('payment_option')
            billing_address = Address(
              user=self.request.user,
              apartment_address = billing_address2,
              street_address =  billing_address1,
              zip_code = shipping_zip,
              country = billing_country,
              address_type="B" 
            )
            billing_address.save()
            order.billing_address = billing_address
            order.save()
        
            set_default_billing = form.cleaned_data.get("set_default_billing")
        
            if set_default_billing:
              billing_address.default = True
              billing_address.save()
          
          else:
            messages.info(self.request, 'Please fill in the required  shipping  address fields')     
        payment_option = form.cleaned_data.get("payment_option")
      #   # TODO: add a redrect to the selected payment option     
        if payment_option == "S":
          return redirect("payment", payment_option="stripe")
        elif payment_option == "P":
          return redirect("paypal")
        else:
          messages.warning(self.request, "Invalid payment option selected")
          return redirect("checkout")
      
      # messages.warning(self.request, 'Failed checkout')
      # return redirect("checkout")
    except ObjectDoesNotExist:
      messages.error(self.request, 'You do not have any active order')
    return redirect("order")


class PaypalView(LoginRequiredMixin, View):
  
  def get(self, *args,**kwargs):
    try:
      form = CheckOutForm()
      order = Order.objects.get(user=self.request.user, ordered=False)
      couponform=CouponForm()
      context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }      
      return render(self.request, 'paypal.html', context)
      
    except ObjectDoesNotExist:
      messages.warning(self.request, 'You d not have any active order')
      return redirect("checkout")
  
  def post(self, *args, **kwargs):
    order= Order.objects.get(user=self.request.user, ordered=False)
    amount = int(order.get_total())
    
    
    try:
            
    # create payment 
      payment = Payment()
      payment.user  = self.request.user
      payment.amount = order.get_total() 
      payment.save()
      
      # for saving the order_item after payment is  made
      order_items = order.items.all()
      order_items.update(ordered=True)
      for item in order_items:
        item.save()
      
      # assigning the payment to the order
      order.ordered = True
      order.payment = payment
      order.ref_code = create_ref_code()
      order.save()
      
      messages.success(self.request, "Your order was successful")
      return redirect('/')
    except ObjectDoesNotExist:
      return redirect("/")

def home(request):
  form = PayPalPaymentsForm()
  if form.is_valid():
    form.save()
    return redirect("https://www.sandbox.paypal.com/cgi-bin/webscr")
  return render(request, 'payment_paypal.html', {'form': form})


class PaymentView(View):
  def get(self, *args, **kwargs):
    order= Order.objects.get(user=self.request.user, ordered=False)
    if  order.billing_address:
      return render(self.request, 'payment.html', {'order':order, 'DISPLAY_COUPON_FORM': False })
    else:
      messages.warning(self.request, 'You have not selected a billing address')
      return redirect("checkout")
  
  def post(self, *args, **kwargs):
    order= Order.objects.get(user=self.request.user, ordered=False)
    amount = int(order.get_total() * 100)
    token = self.request.POST.get("stripeToken")
    
    try:
      # make use of stripe Library
      charge = stripe.Charge.create( amount=amount, currency="usd", source=token)
      
    # create payment 
      payment = Payment()
      payment.stripe_charge_id = charge['id']
      payment.user  = self.request.user
      payment.amount = order.get_total() 
      payment.save()
      
      # for saving the order_item after payment is  made
      order_items = order.items.all()
      order_items.update(ordered=True)
      for item in order_items:
        item.save()
      
      # assigning the payment to the order
      order.ordered = True
      order.payment = payment
      order.ref_code = create_ref_code()
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
      return redirect("/")
  
    messages.warning(self.request, "Invalid data received")
    return redirect("/payment/stripe/")


def get_coupon(request, code):
  try:
    coupon = Coupon.objects.get(code=code)
    return coupon
  except ObjectDoesNotExist:
    messages.warning(request, "This coupon does not exist")
    return redirect("checkout"
                    )
    

class AddCouponView(View):
  def get(self, *args, **kwargs):
      form = CouponForm(self.request.POST or None)
      if  form.is_valid():
        try: 
          code = form.cleaned_data.get("code")   
          order = Order.objects.get(user=self.request.user, ordered=False)
          order.coupon = get_coupon(self.request, code)
          order.save()
          messages.success(self.request, "Succesfuly Added Coupon")
          return redirect("checkout")
        
        except ObjectDoesNotExist:
          messages.info(request, "You do not have an active order")
          return redirect("checkout")

# def add_coupon(request):
#   if request.method =='POST':
#       form = CouponForm(request.POST or None)
#       if  form.is_valid():
#         try: 
#           code = form.cleaned_data.get("code")   
#           order = Order.objects.get(user=request.user, ordered=False)
#           order.coupon = get_coupon(request, code)
#           order.save()
#           messages.success(request, "Succesfuly Added Coupon")
#           return redirect("checkout")
        
#         except ObjectDoesNotExist:
#           messages.info(request, "You do not have an active order")
#           return redirect("checkout")
#   # TODO raise error 
#   return None


class RequestRefundView(View):
  def get(self, *args, **kwargs):
    return render(self.request, 'request_refund.html', {'form': RefundForm()})
  
  def post(self, *args, **kwargs):
    form = RefundForm(self.request.POST or None)
    if form.is_valid():
      ref_code = form.cleaned_data.get("ref_code")
      message = form.cleaned_data.get("message")
      email = form.cleaned_data.get("email")
      # edit the order
      
      try:
        order = Order.objects.get(ref_code=ref_code)
        order.refund_requested = True
        order.save()
        
      # store the refund
        refund = Refund()
        refund.order = order
        refund.reason = message
        refund.email = email
        refund.save()

        messages.info(self.request, 'Your request was received')
        return redirect('request_refund')
      
      except ObjectDoesNotExist:
        messages.info(self.request, "This order does not exist")
        return redirect('request_refund')