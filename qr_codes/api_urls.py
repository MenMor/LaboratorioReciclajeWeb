from django.urls import path
from .views import RecyclableListCreate, RecyclingTransactionListCreate, QRCodeListCreate, UserPointsListCreate, verify_qr_code

urlpatterns = [
    path('recyclables/', RecyclableListCreate.as_view(), name='recyclable-list'),
    path('transactions/', RecyclingTransactionListCreate.as_view(), name='transaction-list'),
    path('qrcodes/', QRCodeListCreate.as_view(), name='qrcode-list'),
    path('userpoints/', UserPointsListCreate.as_view(), name='userpoints-list'),
    path('verify_qr_code/', verify_qr_code, name='verify_qr_code'),
]
