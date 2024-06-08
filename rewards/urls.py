# rewards/urls.py

from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.reward_list), name='reward_list'),
    path('create/', login_required(views.reward_create), name='reward_create'),
    path('update/<int:pk>/', login_required(views.reward_update), name='reward_update'),
    path('delete/<int:pk>/', login_required(views.reward_delete), name='reward_delete'),
]
