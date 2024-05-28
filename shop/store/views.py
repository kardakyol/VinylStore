from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from .forms import UserForm, ShippingForm, OrderPaymentForm
from django.db import transaction
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

class CustomLogoutView(LogoutView):
    template_name = 'logout_form.html'
    next_page = reverse_lazy('store')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            create_customer(user)
            login(request, user)
            return redirect('store')
    else:
        form = SignUpForm()
    return render(request, 'store/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            create_customer(user)
            if user is not None:
                login(request, user)
                return redirect('store')

            else:
                messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    else:
        form = AuthenticationForm()

    return render(request, 'store/login.html', {'form': form})

def create_customer(user):
    if not hasattr(user, 'customer'):
        Customer.objects.create(user=user, email=user.email)

@login_required
def cart_view(request):
    return render(request, 'store/cart.html')


@login_required
def profile_view(request):
    customer = request.user.customer
    context = {
        'customer': customer,
    }
    return render(request, 'store/profile.html', context)

@login_required
def order_history_view(request):
    customer = request.user
    orders = Order.objects.filter(customer=customer, complete=True)
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_history.html', context)

def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    for item in items:
        product = item.product
        quantity_in_cart = item.quantity
        if quantity_in_cart > product.quantity:
            messages.error(request, f"{product.name} is out of stock.")

    if not items:
        messages.info(request, 'Your cart is empty. Please add some items to proceed.')

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    user = request.user

    for item in items:
        product = item.product
        quantity_in_cart = item.quantity
        if quantity_in_cart > product.quantity:
            messages.error(request, f"{product.name} is out of stock. Please remove it from your cart.")
            return redirect('cart')

    if not items:
        messages.info(request, 'Your cart is empty. Please add some items to proceed.')
        return redirect('cart')



    # POST isteği işleniyor
    if request.method == "POST":
        if user.is_authenticated:
            customer = user.customer
            shipping_form = ShippingForm(request.POST)
            payment_form = OrderPaymentForm(request.POST)
            if shipping_form.is_valid() and payment_form.is_valid():
                shipping_address = shipping_form.save(commit=False)
                shipping_address.customer = customer
                shipping_address.order = order
                shipping_address.save()
                payment = payment_form.save(commit=False)
                payment.order = order
                payment.shippingaddress = shipping_address
                payment.save()
                order.checkout()
                return redirect('success')
            else:
                messages.error(request, 'Invalid form data.')
        else:
            messages.error(request, 'You must be logged in to complete the order.')
            return redirect('login')


    else:
        if user.is_authenticated:
            customer = user.customer if hasattr(user, 'customer') else Customer.objects.create(user=user, email=user.email)
        else:
            customer = None

        shipping_form = ShippingForm()
        payment_form = OrderPaymentForm()

        context = {
            'items': items,
            'order': order,
            'cartItems': cartItems,
            'shipping_form': shipping_form,
            'payment_form': payment_form,
        }
        return render(request, 'store/checkout.html', context)

def success(request):
    return render(request, 'store/success.html')


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    # Kullanıcı kimlik doğrulamış mı diye kontrol edin
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        product = Product.objects.get(id=productId)

        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        return JsonResponse('Item was added', safe=False)

    else:
        # Kullanıcı kimlik doğrulamadıysa, bu kısmı çerezlerle işleyin
        product = get_object_or_404(Product, id=productId)
        cart = cookieCart(request)

        if action == 'add':
            if productId in cart:
                if product.quantity > 0:  # Ürün miktarı sıfır değilse
                    cart[productId]['quantity'] += 1
                else:
                    messages.error(request, 'This product is out of stock.')  # Ürün miktarı sıfırsa
            else:
                if product.quantity > 0:  # Ürün miktarı sıfır değilse
                    cart[productId] = {'quantity': 1}
                else:
                    messages.error(request, 'This product is out of stock.')  # Ürün miktarı sıfırsa
        elif action == 'remove':
            if productId in cart:
                cart[productId]['quantity'] -= 1

                if cart[productId]['quantity'] <= 0:
                    del cart[productId]

        # Güncellenmiş sepeti çereze geri kaydedin
        response = JsonResponse('Item was added', safe=False)
        response.set_cookie('cart', json.dumps(cart), samesite=None)
        return response

@transaction.atomic
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)