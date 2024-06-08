from django.urls import path
from .views import EventListCreate, EventDetail, UserEventListCreate, UserEventDetail

urlpatterns = [
    path('', EventListCreate.as_view(), name='event-list-create'),
    path('<int:pk>/', EventDetail.as_view(), name='event-detail'),
    path('userevents/', UserEventListCreate.as_view(), name='userevent-list-create'),
    path('userevents/<int:pk>/', UserEventDetail.as_view(), name='userevent-detail'),
]
