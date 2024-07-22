from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from firebase_admin import db, storage
from django.db import transaction

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateField()
    imageUrl = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        image = kwargs.pop('image', None)
        super().save(*args, **kwargs)
        if image:
            self.upload_image_to_firebase(image)
        self.sync_to_firebase()
        # Guardar en PostgreSQL
        if kwargs.get('using') != 'postgres':
            super().save(using='postgres', *args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Elimina de Firebase
        self.remove_from_firebase()
        # Elimina de la base de datos default
        super().delete(*args, **kwargs)
        # Ahora elimina de PostgreSQL
        if kwargs.get('using') != 'postgres':
            try:
                super().delete(using='postgres', *args, **kwargs)
            except Exception as e:
                # En caso de error, puedes registrar el error o manejarlo de alguna manera
                print(f"Error deleting from PostgreSQL: {e}")

    def upload_image_to_firebase(self, image):
        bucket = storage.bucket()
        blob = bucket.blob(f"event_images/{self.id}/{image.name}")
        blob.upload_from_file(image)
        blob.make_public()
        self.imageUrl = blob.public_url
        super().save(update_fields=['imageUrl'])

    def sync_to_firebase(self):
        ref = db.reference('events').child(str(self.id))
        ref.set({
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat(),
            'imageUrl': self.imageUrl
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

