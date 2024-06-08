from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):

    CORRECT_REPLY_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4')
    ]
    
    correct_reply_index = forms.ChoiceField(choices=CORRECT_REPLY_CHOICES, label='Índice de respuesta correcta')

    class Meta:
        model = Question
        fields = ['question', 'answer1', 'answer2', 'answer3', 'answer4', 'correct_reply_index']
        labels = {
            'question': 'Pregunta',
            'answer1': 'Respuesta 1',
            'answer2': 'Respuesta 2',
            'answer3': 'Respuesta 3',
            'answer4': 'Respuesta 4',
        }