# Generated by Django 3.2.5 on 2022-03-23 00:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0016_league_leagueportfolio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='participants',
            field=models.ManyToManyField(blank=True, default=None, related_name='league_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
