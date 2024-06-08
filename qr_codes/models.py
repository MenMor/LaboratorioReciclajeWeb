from django.db import models
from django.contrib.auth.models import User

class Recyclable(models.Model):
    description = models.CharField(max_length=255)
    value = models.IntegerField()

    def __str__(self):
        return self.description

class RecyclingTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    recyclable = models.ForeignKey(Recyclable, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quantity} - {self.recyclable.description}"

class QRCode(models.Model):
    code = models.CharField(max_length=255)
    transaction = models.ForeignKey(RecyclingTransaction, on_delete=models.CASCADE)

class UserPoints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=255)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(RecyclingTransaction, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"
