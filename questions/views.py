# questions/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Question
from .forms import QuestionForm
from rest_framework import generics
from .serializers import QuestionSerializer
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

def question_list(request):
    questions = Question.objects.all()
    return render(request, 'questions/question_list.html', {'questions': questions})

def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.correct_reply_index = int(form.cleaned_data['correct_reply_index']) - 1
            question.save()
            return redirect('question_list')
    else:
        form = QuestionForm()
    return render(request, 'questions/question_form.html', {'form': form})

def question_update(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.correct_reply_index = int(form.cleaned_data['correct_reply_index']) - 1
            question.save()
            return redirect('question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'questions/question_form.html', {'form': form})

def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question.delete()
        return redirect('question_list')
    return render(request, 'questions/question_confirm_delete.html', {'question': question})

@require_POST
def toggle_enable(request, pk):
    question = get_object_or_404(Question, pk=pk)
    question.enable = not question.enable
    question.save()
    return redirect('question_list')

# Vistas de la API usando DRF
class QuestionListCreate(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    