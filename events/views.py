from django.shortcuts import render, get_object_or_404, redirect
from .models import Event
from .forms import EventForm

from rest_framework import generics
from .models import Event, UserEvent
from .serializers import EventSerializer, UserEventSerializer

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')  # Redirigir a la lista de eventos después de crear
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')  # Redirigir a la lista de eventos después de editar
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})

def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')  # Redirigir a la lista de eventos después de eliminar
    return render(request, 'events/event_confirm_delete.html', {'event': event})


# Vistas de la API usando DRF
class EventListCreate(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class UserEventListCreate(generics.ListCreateAPIView):
    queryset = UserEvent.objects.all()
    serializer_class = UserEventSerializer

class UserEventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserEvent.objects.all()
    serializer_class = UserEventSerializer
    