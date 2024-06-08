from django.urls import path
from .views import RewardListCreate, RewardDetail

urlpatterns = [
    path('', RewardListCreate.as_view(), name='reward-list-create'),
    path('<int:pk>/', RewardDetail.as_view(), name='reward-detail'),
]
