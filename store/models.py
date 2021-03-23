from django.db import models
from django.conf import settings
from django.shortcuts import reverse

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

class Order(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
  items =models.ManyToManyField(OrderItem)
  start_date = models.DateTimeField(auto_now_add=True)
  ordered_date = models.DateTimeField()
  ordered=models.BooleanField(default=False, blank=True, null=True)
  
  
  def __str__(self):
        return self.user.username
      









