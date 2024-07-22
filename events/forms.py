from django import forms
from .models import Event, UserEvent

class EventForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'image']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserEventForm(forms.ModelForm):
    class Meta:
        model = UserEvent
        fields = ['user', 'event']
