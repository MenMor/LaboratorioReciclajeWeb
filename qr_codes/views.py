import qrcode
import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RecyclingTransaction, QRCode, UserPoints
from .forms import QRCodeForm
from .serializers import UserPointsSerializer
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Recyclable, RecyclingTransaction, QRCode, UserPoints
from .serializers import RecyclableSerializer, RecyclingTransactionSerializer, QRCodeSerializer, UserPointsSerializer
import logging

def generate_qr_code(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            qr_code = qrcode.make(f'{transaction.user.username}-{transaction.id}')
            qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
            qr_code_path = os.path.join(qr_code_dir, f'{transaction.user.username}-{transaction.id}.png')

            # Crear el directorio si no existe
            if not os.path.exists(qr_code_dir):
                os.makedirs(qr_code_dir)

            qr_code.save(qr_code_path)

            QRCode.objects.create(code=qr_code_path, transaction=transaction)
            points = transaction.quantity * transaction.recyclable.value
            context = {
                'qr_code_path': f'qr_codes/{transaction.user.username}-{transaction.id}.png',
                'points': points,
                'MEDIA_URL': settings.MEDIA_URL
            }
            return render(request, 'qr_codes/qr_code.html', context)
    else:
        form = QRCodeForm()
    return render(request, 'qr_codes/generate_qr.html', {'form': form})

@api_view(['POST'])
def scan_qr_code(request):
    code = request.data.get('code')
    try:
        qr_code = QRCode.objects.get(code=code)
        transaction = qr_code.transaction
        user = transaction.user
        points = transaction.quantity * transaction.recyclable.value
        
        user_points = UserPoints.objects.create(
            user=user,
            points=points,
            transaction_type='QR Scan',
            transaction=transaction,
            transaction_date=timezone.now()
        )
        
        serializer = UserPointsSerializer(user_points)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except QRCode.DoesNotExist:
        return Response({'error': 'Invalid QR code'}, status=status.HTTP_400_BAD_REQUEST)

# Vistas de la API usando DRF
class RecyclableListCreate(generics.ListCreateAPIView):
    queryset = Recyclable.objects.all()
    serializer_class = RecyclableSerializer

class RecyclingTransactionListCreate(generics.ListCreateAPIView):
    queryset = RecyclingTransaction.objects.all()
    serializer_class = RecyclingTransactionSerializer

class QRCodeListCreate(generics.ListCreateAPIView):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer

class UserPointsListCreate(generics.ListCreateAPIView):
    queryset = UserPoints.objects.all()
    serializer_class = UserPointsSerializer

    def create(self, request, *args, **kwargs):
        logging.info("Request data: %s", request.data)  # Log the received data

        user_id = request.data.get('userId')
        points_to_add = request.data.get('points')
        transaction_type = request.data.get('transaction_type')
        transaction_id = request.data.get('transaction')

        if user_id is None or points_to_add is None or transaction_type is None or transaction_id is None:
            logging.error("Missing required fields: userId, points, transaction_type, or transaction")
            return Response({"error": "userId, points, transaction_type, and transaction are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logging.error("User not found: %s", user_id)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Sum points to existing points or create new entry if it doesn't exist
        user_points, created = UserPoints.objects.get_or_create(
            user=user,
            transaction_type=transaction_type,
            transaction_id=transaction_id,
            defaults={'points': 0}
        )
        user_points.points += int(points_to_add)
        user_points.save()

        serializer = self.get_serializer(user_points)
        logging.info("Updated user points: %s", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    