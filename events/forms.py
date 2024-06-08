from django import forms
from .models import Event, UserEvent

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserEventForm(forms.ModelForm):
    class Meta:
        model = UserEvent
        fields = ['user', 'event']
