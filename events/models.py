from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from firebase_admin import db

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateField()

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('events').child(str(self.id))
        ref.set({
            'id':self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat()
        })

    def remove_from_firebase(self):
        ref = db.reference('events').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=Event)
def sync_event_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=Event)
def remove_event_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()



class UserEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.event.title}'
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('user_events').child(str(self.id))
        ref.set({
            'id':self.id,
            'user': self.user.username,
            'event': self.event.title,
            'registered_at': self.registered_at.isoformat()
        })

    def remove_from_firebase(self):
        ref = db.reference('user_events').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=UserEvent)
def sync_user_event_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=UserEvent)
def remove_user_event_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()

