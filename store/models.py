from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from PIL import Image

# Create your models here.


CATEGORY_CHOICES = (
  ("S", "Shirt"),
  ("SW","SportWear"),
  ("OW", "OutWear")
)

LABEL_CHOICES = (
  ("P", "primary"),
  ("D","danger"),
  ("S", "secondary")
)

class Item(models.Model):
  title = models.CharField(max_length=100,  null=True)
  price = models.FloatField()
  discounted_price = models.FloatField(blank=True, null=True)
  category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
  label = models.CharField(choices=LABEL_CHOICES, max_length=1)
  slug = models.SlugField()
  description = models.TextField() 
  image = models.ImageField(blank=True, null=True)
  
  @property
  def imageUrl(self):
      try:
          url = self.image.url
      except:
          url = ''
      return url
  
  def __str__(self):
    return self.title
  
  def get_absolute_url(self):
    return reverse('product', kwargs={'slug': self.slug})
  
  def get_add_to_cart(self):
    return reverse("add_to_cart", kwargs={"slug":self.slug})
  
  def get_remove_from_cart(self):
    return reverse("remove_from_cart", kwargs={"slug": self.slug})
  
class OrderItem(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
  quantity = models.IntegerField(default=1)
  ordered=models.BooleanField(default=False, blank=True, null=True)
  
  def __str__(self):
    return f"{self.quantity} of {self.item.title}"

  def get_total_item_discount(self):
    return self.quantity * self.item.discounted_price
  
  def get_total_item_price(self):
    return self.quantity * self.item.price
  
  def get_amount_saved(self):
    return self.get_total_item_price() - self.get_total_item_discount()    
  
  def get_final_price(self):
    if self.item.discounted_price:
      return self.get_total_item_discount()
    return self.get_total_item_price()
  
  
  
class BillingAddress(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
  street_address = models.CharField(max_length=100)
  apartment_address = models.CharField(max_length=100)
  country = CountryField(multiple=False)
  zip_code  = models.CharField(max_length=100)
  
  def __str__(self):
    return self.user.username

class Payment(models.Model):
  stripe_charge_id = models.CharField(max_length=30)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, blank=True, null=True)
  amount = models.FloatField()
  timestamp = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.user.username
  

class Coupon(models.Model):
  code = models.CharField(max_length = 15)
  amount = models.FloatField()
  
  def __str__(self):
    return self.code

  
class Order(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
  items =models.ManyToManyField(OrderItem) 
  start_date = models.DateTimeField(auto_now_add=True)
  ordered_date = models.DateTimeField()
  ordered=models.BooleanField(default=False, blank=True, null=True)
  billing_address = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, blank=True, null=True)
  payment= models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  coupon= models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
  
  def __str__(self):
        return self.user.username
  
  def get_total(self):
    total = 0
    for order_item in self.items.all():
      total += order_item.get_final_price()
    total -= self.coupon.amount
    return total
  
  def get_total_quantity(self):
    total = 0
    for item in self.items.all():
      total += item.quantity
    return total
  
