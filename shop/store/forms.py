from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer, ShippingAddress, OrderPayment

class UserForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name..'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email..'}),
        }

class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address', 'city', 'state', 'zipcode']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address..'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City..'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State..'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip code..'})
        }

class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = OrderPayment
        fields = ['cardNumber', 'txnId']

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name..'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name..'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email..'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password..'}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password..'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email..'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password..'}))