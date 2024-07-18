from django import forms
from .models import Recyclable
from firebase_admin import db, get_app
from django.contrib.auth.models import User

class QRCodeForm(forms.Form):
    user = forms.ChoiceField(label="Usuario")
    quantity = forms.IntegerField(label="Cantidad")
    recyclable = forms.ChoiceField(label="Reciclable")

    def __init__(self, *args, **kwargs):
        super(QRCodeForm, self).__init__(*args, **kwargs)
        app = get_app()

        # Carga de usuarios desde Firebase
        users_ref = db.reference('users', app=app)
        users_data = users_ref.get()
        if users_data:
            self.fields['user'].choices = [(user_id, user['email']) for user_id, user in users_data.items() if isinstance(user, dict)]

        # Carga de reciclables desde la base de datos local de Django
        self.fields['recyclable'].choices = [(rec.id, rec.description) for rec in Recyclable.objects.all()]
