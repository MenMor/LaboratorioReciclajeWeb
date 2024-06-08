from django.db import models

class Question(models.Model):
    question = models.CharField(max_length=255)
    answer1 = models.CharField(max_length=255)
    answer2 = models.CharField(max_length=255)
    answer3 = models.CharField(max_length=255)
    answer4 = models.CharField(max_length=255)
    correct_reply_index = models.IntegerField()

    def __str__(self):
        return self.question
    