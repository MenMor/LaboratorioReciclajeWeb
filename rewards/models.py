from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from firebase_admin import db

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField()
    image = models.ImageField(upload_to='reward_images', blank=True, null=True)
    expiration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('rewards').child(str(self.id))
        ref.set({
            'name': self.name,
            'description': self.description,
            'points': self.points,
            'image_url': self.image.url if self.image else None,
            'expiration_date': self.expiration_date.isoformat()
        })

    def remove_from_firebase(self):
        ref = db.reference('rewards').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=Reward)
def sync_reward_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=Reward)
def remove_reward_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()