from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from firebase_admin import db

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Recyclable(models.Model):
    description = models.CharField(max_length=255)
    value = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.description
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('recyclables').child(str(self.id))
        ref.set({
            'description': self.description,
            'value': self.value,
            'category': self.category.name if self.category else None,
        })

    def remove_from_firebase(self):
        ref = db.reference('recyclables').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=Recyclable)
def sync_recyclable_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=Recyclable)
def remove_recyclable_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()


class RecyclingTransaction(models.Model):
    user_id = models.CharField(max_length=255, verbose_name="User ID", default='17')
    quantity = models.IntegerField()
    recyclable = models.CharField(max_length=255)  # Assuming this is how you store it
    transaction_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        """Sync this transaction to Firebase."""
        try:
            ref = db.reference('recycling_transactions')
            transaction_data = {
                'user_id': self.user_id,
                'quantity': self.quantity,
                'recyclable': self.recyclable,
                'transaction_date': self.transaction_date.strftime('%Y-%m-%dT%H:%M:%S')
            }
            ref.child(str(self.id)).set(transaction_data)
        except Exception as e:
            print(f"Failed to sync with Firebase: {e}")

    def remove_from_firebase(self):
        """Remove this transaction from Firebase."""
        try:
            ref = db.reference('recycling_transactions')
            ref.child(str(self.id)).delete()
        except Exception as e:
            print(f"Failed to remove from Firebase: {e}")



@receiver(post_save, sender=RecyclingTransaction)
def sync_recycling_transaction_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=RecyclingTransaction)
def remove_recycling_transaction_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()


class QRCode(models.Model):
    code = models.CharField(max_length=255)
    transaction = models.ForeignKey(RecyclingTransaction, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('qr_codes').child(str(self.id))
        ref.set({
            'code': self.code,
            'transaction': self.transaction.id
        })

    def remove_from_firebase(self):
        ref = db.reference('qr_codes').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=QRCode)
def sync_qr_code_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=QRCode)
def remove_qr_code_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()


class UserPoints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=255)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(RecyclingTransaction, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('user_points').child(str(self.id))
        ref.set({
            'user': self.user.username,
            'points': self.points,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat(),
            'transaction': self.transaction.id if self.transaction else None
        })

    def remove_from_firebase(self):
        ref = db.reference('user_points').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=UserPoints)
def sync_user_points_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=UserPoints)
def remove_user_points_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()
