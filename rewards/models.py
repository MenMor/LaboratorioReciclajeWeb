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
    image_url = models.URLField(max_length=200, blank=True, null=True)
    expiration_date = models.DateTimeField(default=timezone.now)
    category_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image and not self.image_url:
            self.image_url = self.upload_image_to_firebase()
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('rewards').child(str(self.id))
        ref.set({
            'id':self.id,
            'name': self.name,
            'description': self.description,
            'points': self.points,
            'image_url': self.image_url,
            'expiration_date': self.expiration_date.isoformat(),
            'category': self.category_name,
            'quantity': self.quantity
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

# Definición del modelo SecondaryCategory para la segunda base de datos
class SecondaryCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=180)
    image = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'categories'
        managed = False 
        app_label = 'rewards'

    def __str__(self):
        return self.name