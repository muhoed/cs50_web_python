# Generated by Django 3.2.6 on 2021-11-07 07:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0028_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='related',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auctions.message', verbose_name='initial message'),
        ),
    ]