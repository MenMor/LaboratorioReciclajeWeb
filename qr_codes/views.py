import qrcode
import os
from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .forms import QRCodeForm
from django.utils import timezone
from firebase_admin import db, get_app
from django.http import Http404
from rest_framework import generics
from .models import Recyclable, RecyclingTransaction, QRCode, UserPoints
from .serializers import RecyclableSerializer, RecyclingTransactionSerializer, QRCodeSerializer, UserPointsSerializer
from .models import QRCode
from django.http import JsonResponse
import uuid
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

def generate_qr_code(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user']
            quantity = form.cleaned_data['quantity']
            recyclable_id = form.cleaned_data['recyclable']

            # Get data from Firebase
            app = get_app()
            user_ref = db.reference(f'users/{user_id}', app=app)
            user_data = user_ref.get()
            user_email = user_data['email']

            recyclables_ref = db.reference(f'recyclables/{recyclable_id}', app=app)
            recyclable_data = recyclables_ref.get()
            recyclable_value = recyclable_data['value']

            total_points = quantity * recyclable_value

            # Generate unique QR code value
            qr_unique_value = str(uuid.uuid4())
            qr_data = f'{qr_unique_value}'
            qr_img = qrcode.make(qr_data)
            qr_code_path = os.path.join(settings.MEDIA_ROOT, f'qr_codes/{qr_data}.png')
            if not os.path.exists(os.path.dirname(qr_code_path)):
                os.makedirs(os.path.dirname(qr_code_path))
            qr_img.save(qr_code_path)

            # Update user points
            #user_points_ref = user_ref.child('points')
            #current_points_data = user_points_ref.get() or 0

            #if isinstance(current_points_data, dict):
            #    current_points = int(current_points_data.get('points', 0))
            #else:
            #    current_points = int(current_points_data)

            #new_points = current_points + total_points
            #user_points_ref.set(new_points)

             # Save QR code information to Firebase
            qr_codes_ref = db.reference('qr_codes', app=app)
            new_qr_code_ref = qr_codes_ref.push({
                'code': qr_unique_value,
                'transaction': {
                    'user_id': user_id,
                    'quantity': quantity,
                    'recyclable': recyclable_id,
                    'points': total_points,
                    'transaction_date': timezone.now().isoformat(),
                    'used': False
                }
            })

            # Create RecyclingTransaction
            recycling_transaction = RecyclingTransaction.objects.create(
                user_id=user_id,
                quantity=quantity,
                recyclable=recyclable_id,
                transaction_date=timezone.now()
            )

            qr_code_path = os.path.join('qr_codes', f'{qr_data}.png')
            context = {
                'qr_code_path': qr_code_path,
                'points': total_points,
                'form': QRCodeForm()
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
        user_id = transaction.user_id
        points = transaction.quantity * transaction.recyclable.value  # Ensure this returns an integer

        app = get_app()  # Obtain the Firebase instance
        user_ref = db.reference(f'users/{user_id}', app=app)
        user_points_ref = user_ref.child('points')

        current_points_data = user_points_ref.get() or 0

        # Check if the returned data is a dictionary and extract points, else assume zero points
        if isinstance(current_points_data, dict):
            current_points = current_points_data.get('points', 0)
        elif isinstance(current_points_data, int):
            current_points = current_points_data
        else:
            current_points = 0  # Default to 0 if data is in an unexpected format

        new_points = current_points + points
        user_points_ref.set(new_points)  # Update the points in Firebase

        return Response({'message': 'QR code scanned successfully', 'new_points': new_points}, status=status.HTTP_201_CREATED)
    except QRCode.DoesNotExist:
        return Response({'error': 'Invalid QR code'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_qr_code(request):
    qr_code_text = request.data.get('qr_code')
    user_id = request.data.get('user_id')

    try:
        app = get_app()
        qr_code_ref = db.reference(f'qr_codes', app=app)
        qr_code_data = qr_code_ref.order_by_child('code').equal_to(qr_code_text).get()

        if not qr_code_data:
            return JsonResponse({'message': 'Invalid QR Code', 'status': 'error'}, status=404)

        for key, value in qr_code_data.items():
            if value['code'] == qr_code_text:
                transaction_id = value.get('transaction')
                if transaction_id:
                    transaction_ref = db.reference(f'recycling_transactions/{transaction_id}', app=app)
                    transaction_data = transaction_ref.get()
                    user_ref = db.reference(f'users/{user_id}', app=app)
                    user_data = user_ref.get()

                    if not user_data:
                        return JsonResponse({'message': 'User not found', 'status': 'error'}, status=404)

                    if str(transaction_data['user_id']) == str(user_id):
                        points = transaction_data['quantity'] * transaction_data['recyclable']['value']

                        # Update user points in Firebase
                        user_points_ref = user_ref.child('points')
                        current_points_data = user_points_ref.get() or 0

                        if isinstance(current_points_data, dict):
                            current_points = current_points_data.get('points', 0)
                        elif isinstance(current_points_data, int):
                            current_points = current_points_data
                        else:
                            current_points = 0  # Default to 0 if data is in an unexpected format

                        new_points = current_points + points
                        user_points_ref.set({'points': new_points})

                        return JsonResponse({'message': 'QR Code verified and points added', 'status': 'success', 'new_points': new_points}, status=200)
                    else:
                        return JsonResponse({'message': 'QR Code does not match user', 'status': 'error'}, status=400)

    except Exception as e:
        return JsonResponse({'message': str(e), 'status': 'error'}, status=500)

    return JsonResponse({'message': 'Invalid QR Code', 'status': 'error'}, status=404)


@csrf_protect
@api_view(['POST'])
def update_user_points(request):
    qr_code = request.data.get('qr_code')
    user_id = request.data.get('user_id')

    try:
        # Verificar QR code
        qr_code_ref = db.reference('qr_codes')
        qr_code_data = qr_code_ref.order_by_child('code').equal_to(qr_code).get()

        if not qr_code_data:
            return Response({'message': 'Invalid QR Code', 'status': 'error'}, status=status.HTTP_404_NOT_FOUND)

        for key, value in qr_code_data.items():
            if value['code'] == qr_code:
                transaction_id = value.get('transaction')
                if transaction_id:
                    transaction_ref = db.reference(f'recycling_transactions/{transaction_id}')
                    transaction_data = transaction_ref.get()
                    user_ref = db.reference(f'users/{user_id}')
                    user_data = user_ref.get()

                    if not user_data:
                        return Response({'message': 'User not found', 'status': 'error'}, status=status.HTTP_404_NOT_FOUND)

                    if str(transaction_data['user_id']) == str(user_id):
                        points = transaction_data['quantity'] * transaction_data['recyclable']['value']

                        # Actualizar puntos del usuario en Firebase
                        user_points_ref = user_ref.child('points')
                        current_points_data = user_points_ref.get() or 0

                        if isinstance(current_points_data, dict):
                            current_points = current_points_data.get('points', 0)
                        elif isinstance(current_points_data, int):
                            current_points = current_points_data
                        else:
                            current_points = 0  # Default to 0 if data is in an unexpected format

                        new_points = current_points + points
                        user_points_ref.set({'points': new_points})

                        return Response({'message': 'QR Code verified and points added', 'status': 'success', 'new_points': new_points}, status=status.HTTP_200_OK)
                    else:
                        return Response({'message': 'QR Code does not match user', 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': str(e), 'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Invalid QR Code', 'status': 'error'}, status=status.HTTP_404_NOT_FOUND)

# API Views
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