#events/urls.py
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.event_list), name='event_list'),
    path('new/', login_required(views.event_create), name='event_create'),
    path('edit/<int:pk>/', login_required(views.event_edit), name='event_edit'),
    path('delete/<int:pk>/', login_required(views.event_delete), name='event_delete'),
]