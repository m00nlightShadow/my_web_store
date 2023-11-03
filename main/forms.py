from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm

from main.models import MyUser, Product, ProductReturn


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


class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity', min_value=1)


class ProductReturnForm(ModelForm):
    class Meta:
        model = ProductReturn
        fields = []
