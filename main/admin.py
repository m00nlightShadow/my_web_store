from django.contrib import admin
from .models import MyUser, Product, Purchase, ProductReturn

admin.site.register(MyUser)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(ProductReturn)

