# Generated by Django 3.1.7 on 2021-04-19 20:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210416_0945'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='_status',
            new_name='status',
        ),
        migrations.AlterField(
            model_name='listing',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
