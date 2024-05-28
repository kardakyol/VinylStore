import json
from .models import *


from .models import Order, Product  # varsayılan olarak eklenmesi gereken modeller

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'id': product.id,
                'product': {'id': product.id, 'name': product.name, 'price': product.price,
                            'imageURL': product.imageURL}, 'quantity': cart[i]['quantity'],
                'digital': product.digital, 'get_total': total,
            }
            items.append(item)

            if not product.digital:
                order['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}

def cartData(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        customer = None
        cookie_data = cookieCart(request)
        cartItems = cookie_data['cartItems']
        order = cookie_data['order']
        items = cookie_data['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
        defaults={'name': name}
    )

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )
    return customer, order