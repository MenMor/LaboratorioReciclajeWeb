from django.test import TestCase, Client
from django.urls import reverse
from .models import Event
from .forms import EventForm

class EventViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.event = Event.objects.create(name='Test Event', description='This is a test event')

    def test_event_list_view(self):
        response = self.client.get(reverse('event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.name)
    
    def test_event_create_view(self):
        response = self.client.post(reverse('event_create'), {
            'name': 'New Event',
            'description': 'This is a new event',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(name='New Event').exists())

    def test_event_edit_view(self):
        response = self.client.post(reverse('event_edit', args=[self.event.id]), {
            'name': 'Updated Event',
            'description': 'This is an updated event',
        })
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, 'Updated Event')
        self.assertEqual(response.status_code, 302)

    def test_event_delete_view(self):
        response = self.client.post(reverse('event_delete', args=[self.event.id]))
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
        self.assertEqual(response.status_code, 302)
