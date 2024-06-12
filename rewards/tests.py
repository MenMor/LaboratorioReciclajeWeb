from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Reward
from django.contrib.auth.models import User

class RewardModelTest(TestCase):
    def setUp(self):
        self.reward = Reward.objects.create(
            name='Reward Test',
            description='This is a test reward',
            points=100,
            expiration_date=timezone.now()
        )

    def test_reward_creation(self):
        self.assertEqual(self.reward.name, 'Reward Test')
        self.assertEqual(self.reward.description, 'This is a test reward')
        self.assertEqual(self.reward.points, 100)

    def test_reward_str(self):
        self.assertEqual(str(self.reward), 'Reward Test')


class RewardListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.reward = Reward.objects.create(
            name='Reward Test',
            description='This is a test reward',
            points=100,
            expiration_date=timezone.now()
        )

    def test_reward_list_view(self):
        response = self.client.get(reverse('reward_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.reward.name)


class RewardCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_reward_create_view(self):
        response = self.client.post(reverse('reward_create'), {
            'name': 'New Reward',
            'description': 'This is a new reward',
            'points': 200,
            'expiration_date': timezone.now()
        }, follow=True)
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(Reward.objects.filter(name='New Reward').exists())


class RewardUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.reward = Reward.objects.create(
            name='Reward Test',
            description='This is a test reward',
            points=100,
            expiration_date=timezone.now()
        )

    def test_reward_update_view(self):
        response = self.client.post(reverse('reward_update', args=[self.reward.id]), {
            'name': 'Updated Reward',
            'description': 'This is an updated reward',
            'points': 150,
            'expiration_date': timezone.now()
        }, follow=True)
        self.reward.refresh_from_db()
        self.assertEqual(self.reward.name, 'Updated Reward')
        self.assertEqual(response.status_code, 302)  # Should redirect after update


class RewardDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.reward = Reward.objects.create(
            name='Reward Test',
            description='This is a test reward',
            points=100,
            expiration_date=timezone.now()
        )

    def test_reward_delete_view(self):
        response = self.client.post(reverse('reward_delete', args=[self.reward.id]), follow=True)
        self.assertFalse(Reward.objects.filter(id=self.reward.id).exists())
        self.assertEqual(response.status_code, 302)  # Should redirect after deletion
