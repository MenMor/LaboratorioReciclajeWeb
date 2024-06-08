from django import forms
from .models import RecyclingTransaction

class QRCodeForm(forms.ModelForm):
    class Meta:
        model = RecyclingTransaction
        fields = ['user', 'quantity', 'recyclable']
        labels = {
            'user': 'Usuario',
            'quantity': 'Cantidad',
            'recyclable': 'Reciclable'
        }
