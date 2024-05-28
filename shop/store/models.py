from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.full_name()
class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    categories = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.FloatField()
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def order_product(self, quantity):
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.save()
            return True
        return False

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        if self.customer:
            return f"{self.customer.customer.full_name()} @ {self.id}"

    @property
    def shipping(self):
        shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def checkout(self):
        if self.complete == False:
            orderitems = self.orderitem_set.all()
            for item in orderitems:
                product = item.product
                product.order_product(item.quantity)
            self.complete = True
            self.save()

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " ".join([self.address, self.city, self.state, str(self.zipcode)])


class OrderPayment(models.Model):
    cardNumber = models.BigIntegerField()
    txnId = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shippingaddress = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)