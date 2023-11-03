from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class MyUser(AbstractUser):
    money = models.DecimalField(max_digits=10, decimal_places=2, default=10000)


class Product(models.Model):
    title = models.CharField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='main/static/product_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Purchase(models.Model):
    purchased_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='purchase_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_product')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} bought by {self.user} at {self.purchased_at}"


class ProductReturn(models.Model):
    product = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='return_product')
    request_return = models.DateTimeField(auto_now_add=True)
