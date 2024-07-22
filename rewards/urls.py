# rewards/urls.py

from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.reward_list), name='reward_list'),
    path('create/', login_required(views.reward_create), name='reward_create'),
    path('update/<int:pk>/', login_required(views.reward_update), name='reward_update'),
    path('delete/<int:pk>/', login_required(views.reward_delete), name='reward_delete'),
    path('redeem/<int:reward_id>/', login_required(views.redeem_reward_form), name='redeem_reward_form'),
    path('redeem/<int:reward_id>/<str:user_email>/', login_required(views.redeem_reward), name='redeem_reward'),
]
