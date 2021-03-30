from django.contrib import admin
from .models import *


def make_refund_accepted(modelAdmin, request, queryset):
  queryset.update(refund_requested=False, refund_granted=True)
make_refund_accepted.short_description = 'Update orders  to refund granted'

def being_delivered_update(modelAdmin, request, queryset):
    queryset.update(being_delivered = True)
being_delivered_update.short_description = 'being delivered'
  
class OrderAdmin(admin.ModelAdmin):
  list_display=['user', 'ordered', 'being_delivered', 'refund_requested', 'refund_granted', 'received','payment', 'billing_address', 'coupon' ]
  
  list_display_links = ['user', 'payment', 'billing_address', 'coupon']
  
  list_filter = ['ordered', 'being_delivered', 'refund_requested', 'refund_granted', 'received']
  
  search_fields = ['user__username', 'ref_code']
  
  actions = [make_refund_accepted, being_delivered_update]

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)

# Register your models here.
