from django.urls import path

from main.views import HomeView, UserLoginView, UserRegisterView, UserLogoutView, AddProductView, UpdateProductView, \
    PurchaseView, PurchaseListView, ProductReturnView, ProdReturnListView, ApplyProductReturn, DeleteProductReturn

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('purchase/<int:pk>/', PurchaseView.as_view(), name='purchase_product'),
    path('purchases/', PurchaseListView.as_view(), name='purchases'),
    path('product-return/<int:pk>', ProductReturnView.as_view(), name='product_return'),
    path('add-products/', AddProductView.as_view(), name='add_products'),
    path('update-product/<int:pk>/', UpdateProductView.as_view(), name='update_product'),
    path('refunds/', ProdReturnListView.as_view(), name='refunds'),
    path('apply-return/<int:pk>/', ApplyProductReturn.as_view(), name='apply_return'),
    path('reject-return/<int:pk>/', DeleteProductReturn.as_view(), name='reject_return'),
]
