from django.urls import path
from .views import index, dashboard_by_location

urlpatterns = [
    path('', index, name='dashboard_index'),
    path('location/', dashboard_by_location, name='dashboard_by_location'),
]
