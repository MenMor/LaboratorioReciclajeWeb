# rewards/serializers.py
from rest_framework import serializers
from .models import Reward

class RewardSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')

    class Meta:
        model = Reward
        fields = ['id', 'name', 'description', 'points', 'image_url', 'expiration_date', 'category']
