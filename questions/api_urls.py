from django.urls import path
from .views import QuestionListCreate, QuestionDetail

urlpatterns = [
    path('', QuestionListCreate.as_view(), name='question-list-create'),
    path('<int:pk>/', QuestionDetail.as_view(), name='question-detail'),
]
