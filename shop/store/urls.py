from . import views
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy


urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('checkout/success/', views.success, name="success"),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('store')), name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('profile/', views.profile_view, name='profile'),
    path('order-history/', views.order_history_view, name='order_history')
]