# Generated by Django 5.0.6 on 2024-07-21 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0003_reward_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]