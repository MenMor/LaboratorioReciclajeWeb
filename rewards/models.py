from django.db import models
from django.utils import timezone

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField()
    image = models.ImageField(upload_to='reward_images', blank=True, null=True)
    expiration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    