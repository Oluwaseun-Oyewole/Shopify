from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
  ("S", "Stripe"),
  ("P", "Paypal")
)
  
class CheckOutForm(forms.Form):
  shipping_address = forms.CharField(required=False)
  shipping_address2 = forms.CharField(required=False)
  shipping_country = CountryField( blank_label='(select country)').formfield(required=False, widget=CountrySelectWidget(attrs={
    'class':'custom-select d-block w-100'
  }))
  shipping_zip = forms.CharField(required=False)
  same_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())  
  
  # for billing 
  billing_address = forms.CharField(required=False)
  billing_address2 = forms.CharField(required=False)
  billing_country = CountryField( blank_label='(select country)').formfield(required=False, widget=CountrySelectWidget(attrs={
    'class':'custom-select d-block w-100'
  }))
  billing_zip = forms.CharField(required=False)
  
  set_default_shipping =forms.BooleanField(required=False)
  use_default_shipping =forms.BooleanField(required=False)
  
  set_default_billing =forms.BooleanField(required=False)
  use_default_billing =forms.BooleanField(required=False)

  payment_option = forms.ChoiceField(choices = PAYMENT_CHOICES, widget=forms.RadioSelect())

class CouponForm(forms.Form):
  code = forms.CharField(widget=forms.TextInput(attrs={
    'class': "form-control",
    'placeholder': 'promo code',
    'aria-label':"Recipient's username",
    'aria-describedby':"basic-addon2"
  }))
  

class RefundForm(forms.Form):
  ref_code = forms.CharField()
  message= forms.CharField(widget=forms.Textarea(attrs={
    'rows':4
  }))
  email = forms.EmailField()
  
  
  
  # street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '878 Ajao Estate'}))
  # apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartment or suite'}))
  # country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
  #   'class':'custom-select d-block w-100'
  # }))
  # zip_code = forms.CharField(widget=forms.TextInput(attrs={
  #   'class': 'form-control'
  # }))
  # same_shipping_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())
  # save_info = forms.BooleanField(required=False, widget=forms.CheckboxInput())
  # payment_option = forms.ChoiceField(choices = PAYMENT_CHOICES, widget=forms.RadioSelect())