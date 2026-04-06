from django import forms
from django.forms import CheckboxInput
from accounts.models import ShippingAddress


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'address_line_1': forms.TextInput(attrs={'placeholder': 'Street address, P.O. box'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State / Province / Region'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'ZIP / Postal Code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        }


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'address_type',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
            'is_default',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'address_type': forms.TextInput(attrs={'placeholder': 'Address Type (optional)'}),
            'address_line_1': forms.TextInput(attrs={'placeholder': 'Street address, P.O. box, c/o'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State / Province / Region'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'ZIP / Postal Code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'is_default': CheckboxInput(attrs={'class': 'default-checkbox'}),
        }