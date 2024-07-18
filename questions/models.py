from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from firebase_admin import db

class Question(models.Model):
    question = models.CharField(max_length=255)
    answer1 = models.CharField(max_length=255)
    answer2 = models.CharField(max_length=255)
    answer3 = models.CharField(max_length=255)
    answer4 = models.CharField(max_length=255)
    correct_reply_index = models.IntegerField()
    enable = models.BooleanField(default=True)

    def __str__(self):
        return self.question
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_to_firebase()

    def delete(self, *args, **kwargs):
        self.remove_from_firebase()
        super().delete(*args, **kwargs)

    def sync_to_firebase(self):
        ref = db.reference('questions').child(str(self.id))
        ref.set({
            'id': self.id,
            'question': self.question,
            'answer1': self.answer1,
            'answer2': self.answer2,
            'answer3': self.answer3,
            'answer4': self.answer4,
            'correct_reply_index': self.correct_reply_index,
            'enable': self.enable 
        })

    def remove_from_firebase(self):
        ref = db.reference('questions').child(str(self.id))
        ref.delete()

@receiver(post_save, sender=Question)
def sync_question_to_firebase(sender, instance, **kwargs):
    instance.sync_to_firebase()

@receiver(post_delete, sender=Question)
def remove_question_from_firebase(sender, instance, **kwargs):
    instance.remove_from_firebase()