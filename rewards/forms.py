from django import forms
from .models import Reward, SecondaryCategory

class RewardForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=SecondaryCategory.objects.using('postgres').all(), empty_label="Seleccione una categoría")

    class Meta:
        model = Reward
        fields = ['name', 'description', 'points', 'image', 'expiration_date', 'category', 'quantity']
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'points': 'Puntos',
            'image': 'Imagen',
            'expiration_date': 'Fecha de Expiración',
            'category': 'Categoria',
            'quantity': 'Cantidad',
        }
