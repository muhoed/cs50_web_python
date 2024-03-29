# Generated by Django 3.1.7 on 2021-11-12 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0031_auto_20211112_2243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='topic',
        ),
        migrations.AddField(
            model_name='message',
            name='listing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auctions.listing', verbose_name='listing regarding which the message was sent'),
        ),
        migrations.AlterField(
            model_name='message',
            name='subject',
            field=models.CharField(default='Old message', max_length=285, verbose_name='message subject'),
            preserve_default=False,
        ),
    ]
