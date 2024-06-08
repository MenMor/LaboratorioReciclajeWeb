from django.urls import path
from .views import RecyclableListCreate, RecyclingTransactionListCreate, QRCodeListCreate, UserPointsListCreate

urlpatterns = [
    path('', QRCodeListCreate.as_view(), name='qrcode-list-create'),  # Root path for QR codes
    path('recyclables/', RecyclableListCreate.as_view(), name='recyclable-list-create'),
    path('transactions/', RecyclingTransactionListCreate.as_view(), name='transaction-list-create'),
    path('qrcodes/', QRCodeListCreate.as_view(), name='qrcode-list-create'),  # Optional detailed path for QR codes
    path('userpoints/', UserPointsListCreate.as_view(), name='userpoints-list-create'),
]
