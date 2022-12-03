# Generated by Django 3.1.7 on 2022-11-26 23:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='viewers_list',
            field=models.ManyToManyField(related_name='viewed', through='network.ViewedPost', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_comments', to='network.user'),
        ),
    ]
