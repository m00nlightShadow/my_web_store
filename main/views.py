from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, CreateView, UpdateView, ListView, DeleteView
from main.forms import RegistrationForm, ProductForm, ProductReturnForm, PurchaseForm
from main.mixins import StaffRequiredMixin
from main.models import Product, Purchase, ProductReturn
from django.contrib import messages


class HomeView(ListView):
    model = Product
    template_name = 'main/home.html'
    context_object_name = 'product_list'
    extra_context = {'purchase_form': PurchaseForm}


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


class PurchaseView(LoginRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request, 'product_pk': self.kwargs.get('pk')})
        return kwargs

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse('home'))

    def form_valid(self, form):
        product = form.product
        quantity = form.cleaned_data.get('quantity')
        total_price = product.price * quantity
        purchase = form.save(commit=False)
        purchase.product = product
        purchase.user = self.request.user
        product.stock -= quantity
        self.request.user.money -= total_price
        with transaction.atomic():
            purchase.save()
            product.save()
            self.request.user.save()
        messages.success(self.request, 'Successful!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')


class AddProductView(StaffRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/admin/add_products.html'

    def get_success_url(self):
        return reverse('add_products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context


class UpdateProductView(StaffRequiredMixin, UpdateView):
    queryset = Product.objects.all()
    form_class = ProductForm
    template_name = 'main/admin/update_product.html'

    def get_success_url(self):
        return reverse('add_products')


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'main/user/purchase_list.html'
    context_object_name = 'purchase_list'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)


class ProductReturnView(LoginRequiredMixin, CreateView):
    model = ProductReturn
    form_class = ProductReturnForm
    template_name = 'main/user/return_product.html'
    success_url = reverse_lazy('purchases')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request, 'purchase_pk': self.kwargs.get('pk')})
        return kwargs

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse('home'))

    def form_valid(self, form):
        product_return = form.save(commit=False)
        product_return.product = form.purchase
        product_return.save()
        return super().form_valid(form)


class ProdReturnListView(StaffRequiredMixin, ListView):
    model = ProductReturn
    template_name = 'main/admin/product_returns.html'
    context_object_name = 'return_product_list'


class ApplyProductReturn(StaffRequiredMixin, DeleteView):
    model = ProductReturn
    success_url = reverse_lazy('refunds')

    def post(self, request, *args, **kwargs):
        product_return = self.get_object()
        purchase = product_return.product
        product = purchase.product
        product.stock += purchase.quantity
        user = purchase.user
        user.money += purchase.quantity * product.price
        with transaction.atomic():
            product.save()
            user.save()
            purchase.delete()
            product_return.delete()
        return redirect(self.success_url)


class DeleteProductReturn(StaffRequiredMixin, DeleteView):
    model = ProductReturn
    success_url = reverse_lazy('refunds')

    def post(self, request, *args, **kwargs):
        product_return = self.get_object()
        product_return.delete()
        return redirect(self.success_url)
