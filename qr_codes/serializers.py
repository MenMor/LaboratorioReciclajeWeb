from rest_framework import serializers
from .models import Recyclable, RecyclingTransaction, QRCode, UserPoints

class RecyclableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recyclable
        fields = '__all__'

class RecyclingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecyclingTransaction
        fields = '__all__'

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'

class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = '__all__'
