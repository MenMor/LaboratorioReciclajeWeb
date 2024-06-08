#qr_codes/urls.py
from django.urls import path
from .views import generate_qr_code, scan_qr_code
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('generate_qr/', login_required(generate_qr_code), name='generate_qr'),
    path('scan_qr_code/', login_required(scan_qr_code), name='scan_qr_code'),
]