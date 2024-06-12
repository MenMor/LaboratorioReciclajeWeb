from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from firebase_admin import db

class User(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('users').child(str(self.id))
        ref.set({
            'username': self.username,
            'email': self.email,
            'is_superuser': self.is_superuser,
            'is_staff': self.is_staff,
            'date_joined': self.date_joined.isoformat()
        })

    def remove_from_firebase(self):
        ref = db.reference('users').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=User)
def sync_user_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=User)
def remove_user_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase() 