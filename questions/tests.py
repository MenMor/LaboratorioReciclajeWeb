from django.test import TestCase
from django.urls import reverse
from .models import Question

class QuestionModelTest(TestCase):

    def setUp(self):
        self.question = Question.objects.create(
            question='¿Cuál es tu color favorito?',
            answer1='Rojo',
            answer2='Azul',
            answer3='Verde',
            answer4='Amarillo',
            correct_reply_index=2
        )

    def test_question_creation(self):
        self.assertEqual(self.question.question, '¿Cuál es tu color favorito?')
        self.assertEqual(self.question.answer1, 'Rojo')
        self.assertEqual(self.question.answer2, 'Azul')
        self.assertEqual(self.question.answer3, 'Verde')
        self.assertEqual(self.question.answer4, 'Amarillo')
        self.assertEqual(self.question.correct_reply_index, 2)

    def test_question_str(self):
        self.assertEqual(str(self.question), '¿Cuál es tu color favorito?')

class QuestionListViewTest(TestCase):

    def setUp(self):
        self.question = Question.objects.create(
            question='¿Cuál es tu color favorito?',
            answer1='Rojo',
            answer2='Azul',
            answer3='Verde',
            answer4='Amarillo',
            correct_reply_index=2
        )

    def test_question_list_view(self):
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.question)

class QuestionCreateViewTest(TestCase):

    def test_question_create_view(self):
        response = self.client.post(reverse('question_create'), {
            'question': '¿Cuál es tu color favorito?',
            'answer1': 'Rojo',
            'answer2': 'Azul',
            'answer3': 'Verde',
            'answer4': 'Amarillo',
            'correct_reply_index': 2
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Question.objects.filter(question='¿Cuál es tu color favorito?').exists())

class QuestionUpdateViewTest(TestCase):

    def setUp(self):
        self.question = Question.objects.create(
            question='¿Cuál es tu color favorito?',
            answer1='Rojo',
            answer2='Azul',
            answer3='Verde',
            answer4='Amarillo',
            correct_reply_index=2
        )

    def test_question_update_view(self):
        response = self.client.post(reverse('question_update', args=[self.question.id]), {
            'question': '¿Cuál es tu animal favorito?',
            'answer1': 'Perro',
            'answer2': 'Gato',
            'answer3': 'Pájaro',
            'answer4': 'Pez',
            'correct_reply_index': 1
        })
        self.question.refresh_from_db()
        self.assertEqual(self.question.question, '¿Cuál es tu animal favorito?')
        self.assertEqual(response.status_code, 302)

class QuestionDeleteViewTest(TestCase):

    def setUp(self):
        self.question = Question.objects.create(
            question='¿Cuál es tu color favorito?',
            answer1='Rojo',
            answer2='Azul',
            answer3='Verde',
            answer4='Amarillo',
            correct_reply_index=2
        )

    def test_question_delete_view(self):
        response = self.client.post(reverse('question_delete', args=[self.question.id]))
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())
        self.assertEqual(response.status_code, 302)
