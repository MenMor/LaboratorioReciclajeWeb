# Generated by Django 5.0.6 on 2024-07-18 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0002_category_reward_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]
