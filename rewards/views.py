# rewards/views.py

from django.shortcuts import render, redirect
from .models import Reward, Category
from .forms import RewardForm
from rest_framework import generics
from .serializers import RewardSerializer
from django.shortcuts import render, redirect
from firebase_admin import db, storage
from rest_framework.response import Response

def reward_list(request):
    rewards = Reward.objects.all()
    return render(request, 'rewards/reward_list.html', {'rewards': rewards})

def upload_image_to_firebase(image):
    bucket = storage.bucket()
    blob = bucket.blob(f'reward_images/{image.name}')
    blob.upload_from_filename(image.path)
    blob.make_public()
    return blob.public_url

def reward_create(request):
    if request.method == 'POST':
        form = RewardForm(request.POST, request.FILES)
        if form.is_valid():
            reward = form.save()

            # Subir imagen a Firebase Storage y obtener la URL
            if reward.image:
                image_url = upload_image_to_firebase(reward.image)

            # Actualizar Firebase
            ref = db.reference('rewards')
            ref.child(str(reward.id)).set({
                'id':reward.id,
                'name': reward.name,
                'description': reward.description,
                'points': reward.points,
                'image_url': image_url,
                'expiration_date': reward.expiration_date.isoformat(),
                'category': reward.category.name 
            })

            return redirect('reward_list')
    else:
        form = RewardForm()
    return render(request, 'rewards/reward_form.html', {'form': form})

def reward_update(request, pk):
    reward = Reward.objects.get(pk=pk)
    if request.method == 'POST':
        form = RewardForm(request.POST, request.FILES, instance=reward)
        if form.is_valid():
            reward = form.save()

            # Subir imagen a Firebase Storage y obtener la URL
            if 'image' in request.FILES:
                image_url = upload_image_to_firebase(reward.image)

            # Actualizar Firebase
            ref = db.reference('rewards')
            ref.child(str(reward.id)).update({
                'id':reward.id,
                'name': reward.name,
                'description': reward.description,
                'points': reward.points,
                'image_url': image_url,
                'expiration_date': reward.expiration_date.isoformat(),
                'category': reward.category.name  
            })

            return redirect('reward_list')
    else:
        form = RewardForm(instance=reward)
    return render(request, 'rewards/reward_form.html', {'form': form})

def reward_delete(request, pk):
    reward = Reward.objects.get(pk=pk)
    if request.method == 'POST':
        reward_id = reward.id
        reward.delete()

        # Eliminar de Firebase
        ref = db.reference('rewards')
        ref.child(str(reward_id)).delete()

        return redirect('reward_list')
    return render(request, 'rewards/reward_confirm_delete.html', {'reward': reward})

# Vistas de la API usando DRF
class RewardListCreate(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        rewards_data = serializer.data
        filtered_rewards = [reward for reward in rewards_data if reward.get('id') is not None]
        rewards_dict = {str(reward['id']): reward for reward in filtered_rewards}

        return Response(rewards_dict)

class RewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer