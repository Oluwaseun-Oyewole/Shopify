from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget



PAYMENT_CHOICES = (
  ("S", "Stripe"),
  ("P", "Paypal")
)
  
class CheckOutForm(forms.Form):
  street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '878 Ajao Estate'}))
  apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartment or suite'}))
  country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
    'class':'custom-select d-block w-100'
  }))
  zip_code = forms.CharField(widget=forms.TextInput(attrs={
    'class': 'form-control'
  }))
  same_shipping_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())
  save_info = forms.BooleanField(required=False, widget=forms.CheckboxInput())
  payment_option = forms.ChoiceField(choices = PAYMENT_CHOICES, widget=forms.RadioSelect())
  
  
  #  def get(self, *args,**kwargs):
  #     form = CheckOutForm()
  #   return render(self.request, 'checkout-page.html', {"form": form})
  
  # def post(self, *args, **kwargs):
  #   form = CheckOutForm(self.request.POST or None)
  #   # print(self.request.POST)
  #   try:
  #     order = Order.objects.get(user=self.request.user, ordered=False)
  #     if form.is_valid():
  #       # print(form.cleaned_data)
  #       # print("This is a valid form")
  #       street_address = form.cleaned_data.get['street_address']
  #       apartment_address = form.cleaned_data.get['apartment_address']
  #       country = form.cleaned_data.get['country']
  #       zip_code = form.cleaned_data.get['zip_code']
  #       # TODO: add fuunctionalities for this fields
  #       # same_shipping_address = form.cleaned_data.get['same_shipping_address']
  #       # save_info = form.cleaned_data.get['save_info']
        
  #       payment_option = form.cleaned_data.get['payment_option']
  #       billing_address = BillingAddress(
  #         user=self.request.user,
  #         apartment_address = apartment_address,
  #         street_address =  street_address,
  #         same_shipping_address = same_shipping_address,
  #         payment_option =  payment_option,
  #         save_info = save_info,
  #       )
  #       billing_address.save()
  #       order.billing_address = billing_address
  #       order.save()
  #       # TODO: add a redrect to the redirected paymeny option
  #       return redirect("checkout")
  #     messages.warning(self.request, 'Failed checkout')
  #     return redirect("checkout")
    
  #   except ObjectDoesNotExist:
  #     messages.error(request, 'You do not have any active order')
  #     return redirect("order")
    