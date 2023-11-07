import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone

from main.models import MyUser, Product, ProductReturn, Purchase


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = MyUser
        fields = ['username']
        widgets = {
            'email': forms.EmailInput(),
            'password': forms.PasswordInput(),
        }


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['quantity', ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.product_pk = kwargs.pop('product_pk', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            product = Product.objects.get(pk=self.product_pk)
            self.product = product
        except Product.DoesNotExist:
            messages.error(self.request, 'Product does not exist')
            raise ValidationError('Incorrect product id')
        quantity = cleaned_data['quantity']
        if product.stock < quantity:
            messages.error(self.request, 'Not enough products')
            self.add_error('quantity', 'Not enough products')
        if quantity * product.price > self.request.user.money:
            messages.error(self.request, 'You have not enough money')
            self.add_error(None, 'You have not enough money')


class ProductReturnForm(ModelForm):
    class Meta:
        model = ProductReturn
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.purchase_pk = kwargs.pop('purchase_pk', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        try:
            purchase = Purchase.objects.get(pk=self.purchase_pk)
            purchased_at = purchase.purchased_at
            time_now = timezone.now()
            time_difference = time_now - purchased_at
            if time_difference > datetime.timedelta(seconds=settings.TIME_TO_REFUND):
                messages.info(self.request, "Return time has expired")
                raise ValidationError("Return time has expired")
            self.purchase = purchase
        except Purchase.DoesNotExist:
            messages.error(self.request, 'Purchase does not exist')
            raise ValidationError('Incorrect purchase id')
