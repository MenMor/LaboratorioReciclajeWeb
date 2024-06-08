#questions/urls.py
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.question_list), name='question_list'),
    path('new/', login_required(views.question_create), name='question_create'),
    path('edit/<int:pk>/', login_required(views.question_update), name='question_update'),
    path('delete/<int:pk>/', login_required(views.question_delete), name='question_delete'),
]
