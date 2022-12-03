# Generated by Django 3.1.7 on 2022-11-29 21:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20221129_2211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='following',
        ),
        migrations.AddField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Users the user follows'),
        ),
    ]
