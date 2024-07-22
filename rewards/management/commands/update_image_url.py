# rewards/management/commands/update_image_url.py

from django.core.management.base import BaseCommand
from rewards.models import Reward

class Command(BaseCommand):
    help = 'Actualizar image_url para las recompensas existentes'

    def handle(self, *args, **kwargs):
        rewards = Reward.objects.all()
        for reward in rewards:
            if reward.image and not reward.image_url:
                reward.image_url = reward.image.url
                reward.save()
                self.stdout.write(self.style.SUCCESS(f'Actualizado: {reward.name}'))
