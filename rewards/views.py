# rewards/views.py

from django.shortcuts import render, redirect
from .models import Reward, Category
from .forms import RewardForm
from rest_framework import generics
from .serializers import RewardSerializer
from django.shortcuts import render, redirect
from firebase_admin import db

def reward_list(request):
    rewards = Reward.objects.all()
    return render(request, 'rewards/reward_list.html', {'rewards': rewards})

def reward_create(request):
    if request.method == 'POST':
        form = RewardForm(request.POST, request.FILES)
        if form.is_valid():
            reward = form.save()

            # Actualizar Firebase
            ref = db.reference('rewards')
            ref.child(str(reward.id)).set({
                'name': reward.name,
                'description': reward.description,
                'points': reward.points,
                'image_url': reward.image.url if reward.image else None,
                'expiration_date': reward.expiration_date.isoformat(),
                'category': reward.category.name  # Actualización para incluir la categoría
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

            # Actualizar Firebase
            ref = db.reference('rewards')
            ref.child(str(reward.id)).update({
                'name': reward.name,
                'description': reward.description,
                'points': reward.points,
                'image_url': reward.image.url if reward.image else None,
                'expiration_date': reward.expiration_date.isoformat(),
                'category': reward.category.name  # Actualización para incluir la categoría
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

class RewardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
