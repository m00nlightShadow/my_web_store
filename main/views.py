import datetime

from django.contrib.auth import login
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, CreateView, UpdateView, DetailView, ListView, DeleteView
from main.forms import RegistrationForm, ProductForm, PurchaseForm, ProductReturnForm
from main.models import Product, Purchase, ProductReturn
from django.contrib import messages
from django.utils import timezone


class HomeView(ListView):
    model = Product
    template_name = 'main/home.html'
    context_object_name = 'product_list'


class UserLoginView(LoginView):
    template_name = 'main/user/login.html'

    def get_success_url(self):
        return reverse('home')


class UserRegisterView(FormView):
    form_class = RegistrationForm
    template_name = 'main/user/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.wallet = 10000
        user.save()
        login(self.request, user)
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class PurchaseView(LoginRequiredMixin, DetailView, FormView):
    model = Product
    form_class = PurchaseForm
    template_name = 'main/user/purchase.html'
    context_object_name = 'product'
    raise_exception = True

    def form_valid(self, form):
        quantity = form.cleaned_data['quantity']
        product = self.get_object()
        user = self.request.user
        product_sum = product.price * quantity
        if product.stock < quantity:
            messages.info(self.request, 'Not enough in stock')
        elif user.money < product_sum:
            messages.info(self.request, 'You have not enough money for this purchase')
        else:
            product.stock -= quantity
            product.save()
            user.money -= product_sum
            user.save()
            purchase = Purchase(user=user, product=product, quantity=quantity)
            purchase.save()
            return redirect('purchases')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')


class AddProductView(UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/admin/add_products.html'

    def get_success_url(self):
        return reverse('add_products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class UpdateProductView(UserPassesTestMixin, UpdateView):
    queryset = Product.objects.all()
    form_class = ProductForm
    template_name = 'main/admin/update_product.html'

    def get_success_url(self):
        return reverse('add_products')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class PurchaseListView(ListView):
    model = Purchase
    template_name = 'main/user/purchase_list.html'
    context_object_name = 'purchase_list'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)


class ProductReturnView(CreateView):
    model = ProductReturn
    form_class = ProductReturnForm
    template_name = 'main/user/return_product.html'
    success_url = reverse_lazy('purchases')

    def form_valid(self, form):
        purchase_id = self.kwargs['pk']
        purchase = Purchase.objects.get(pk=purchase_id)
        purchased_at = purchase.purchased_at
        now = timezone.now()
        time_difference = now - purchased_at
        if time_difference < datetime.timedelta(seconds=180):
            return_product = form.save(commit=False)
            return_product.product = purchase
            return_product.save()
            return super().form_valid(form)
        else:
            messages.info(self.request, "Return time has expired")
            return redirect(self.success_url)


class ProdReturnListView(ListView):
    model = ProductReturn
    template_name = 'main/admin/product_returns.html'
    context_object_name = 'return_product_list'


class ApplyProductReturn(DeleteView):
    model = ProductReturn
    success_url = reverse_lazy('refunds')

    def post(self, request, *args, **kwargs):
        product_return = self.get_object()
        purchase = product_return.product

        product = purchase.product
        product.stock += purchase.quantity
        product.save()
        user = purchase.user
        user.money += purchase.quantity * product.price
        user.save()

        purchase.delete()
        product_return.delete()
        return redirect(self.success_url)


class DeleteProductReturn(DeleteView):
    model = ProductReturn
    success_url = reverse_lazy('refunds')

    def post(self, request, *args, **kwargs):
        product_return = self.get_object()
        product_return.delete()
        return redirect(self.success_url)
