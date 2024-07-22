# rewards/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Reward, SecondaryCategory
from .forms import RewardForm
from rest_framework import generics
from .serializers import RewardSerializer
from django.shortcuts import render, redirect
from firebase_admin import db, storage
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage

def reward_list(request):
    rewards = Reward.objects.all()
    return render(request, 'rewards/reward_list.html', {'rewards': rewards})

def upload_image_to_firebase(image_path, image_name):
    bucket = storage.bucket()
    blob = bucket.blob(f'reward_images/{image_name}')
    blob.upload_from_filename(image_path)
    blob.make_public()
    return blob.public_url

def reward_create(request):
    if request.method == 'POST':
        form = RewardForm(request.POST, request.FILES)
        if form.is_valid():
            reward = form.save(commit=False)

            # Obtener la categoría desde la base de datos postgres
            category_id = request.POST.get('category')
            category = get_object_or_404(SecondaryCategory.objects.using('postgres'), id=category_id)
            reward.category_name = category.name  # Guardar el nombre de la categoría

            # Subir imagen a Firebase Storage y obtener la URL
            image_url = None
            if reward.image:
                # Guardar la imagen localmente primero
                image = request.FILES['image']
                image_path = default_storage.save(image.name, image)
                full_image_path = default_storage.path(image_path)

                # Subir la imagen guardada a Firebase
                image_url = upload_image_to_firebase(full_image_path, image.name)

                # Eliminar la imagen local después de subirla
                default_storage.delete(image_path)

            reward.image_url = image_url
            reward.save()

            # Actualizar Firebase
            ref = db.reference('rewards')
            ref.child('null').delete()

            ref.child(str(reward.id)).set({
                'id': reward.id,
                'name': reward.name,
                'description': reward.description,
                'points': reward.points,
                'image_url': image_url,
                'expiration_date': reward.expiration_date.isoformat(),
                'category': reward.category_name,
                'quantity': reward.quantity
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
            reward = form.save(commit=False)

            # Subir imagen a Firebase Storage y obtener la URL si hay una nueva imagen
            if 'image' in request.FILES:
                image = request.FILES['image']
                image_path = default_storage.save(image.name, image)
                full_image_path = default_storage.path(image_path)
                image_url = upload_image_to_firebase(full_image_path, image.name)
                default_storage.delete(image_path)
            else:
                ref = db.reference('rewards')
                existing_data = ref.child(str(reward.id)).get()
                image_url = existing_data.get('image_url') if existing_data else reward.image_url

            reward.image_url = image_url
            reward.save()

            # Actualizar Firebase
            ref = db.reference('rewards')
            ref.child('null').delete()
            ref.child(str(reward.id)).update({
                'id': reward.id,
                'name': reward.name,
                'description': reward.description,
                'points': reward.points,
                'image_url': image_url,
                'expiration_date': reward.expiration_date.isoformat(),
                'category': reward.category_name,
                'quantity': reward.quantity
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

@login_required
def redeem_reward_form(request, reward_id):
    reward = Reward.objects.get(pk=reward_id)
    if request.method == 'POST':
        user_email = request.POST.get('user_email')
        if user_email:
            return redirect('redeem_reward', reward_id=reward_id, user_email=user_email)
    return render(request, 'rewards/redeem_reward_form.html', {'reward': reward})

@login_required
@csrf_exempt
def redeem_reward(request, reward_id, user_email):
    try:
        reward = Reward.objects.get(pk=reward_id)

        if not user_email:
            messages.error(request, 'Invalid user email.')
            return redirect('redeem_reward_form', reward_id=reward_id)

        users_ref = db.reference('users')
        all_users = users_ref.get()
        user_data = None
        user_id = None

        # Buscar usuario por correo electrónico
        for key, value in all_users.items():
            if value.get('email') == user_email:
                user_data = value
                user_id = key
                break

        if user_data is None:
            messages.error(request, 'User not found in Firebase.')
            return redirect('redeem_reward_form', reward_id=reward_id)

        # Extraer los puntos del usuario correctamente
        user_points = user_data.get('points', {}).get('points', 0)
        if user_points >= reward.points and reward.quantity > 0:
            new_user_points = user_points - reward.points
            users_ref.child(user_id).child('points').set({'points': new_user_points})

            # Obtener la URL de la imagen desde Firebase si existe
            reward_ref = db.reference(f'rewards/{reward_id}')
            existing_data = reward_ref.get()
            if existing_data:
                image_url = existing_data.get('image_url', reward.image_url)
            else:
                image_url = reward.image_url

            # Actualizar la cantidad en Firebase y mantener la URL de la imagen
            reward_ref.update({
                'quantity': reward.quantity - 1,
                'image_url': image_url  # Mantener la URL de Firebase
            })

            # Actualizar la recompensa en Django
            reward.quantity -= 1
            reward.image_url = image_url  # Asegurar que no se cambie la URL
            reward.save(update_fields=['quantity', 'image_url'])

            messages.success(request, 'Reward redeemed successfully!')
            return redirect('reward_list')
        else:
            messages.error(request, 'Not enough points or reward out of stock.')
            return redirect('redeem_reward_form', reward_id=reward_id)
    except Exception as e:
        print(f'Error: {e}')
        messages.error(request, 'An error occurred.')
        return redirect('redeem_reward_form', reward_id=reward_id)


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
