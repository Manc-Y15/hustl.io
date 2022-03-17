# Generated by Django 4.0 on 2022-03-14 22:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0012_alter_transaction_stock_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='friends',
            field=models.ManyToManyField(blank=True, default=None, related_name='friends', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='requested_friends',
            field=models.ManyToManyField(blank=True, default=None, related_name='received_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]