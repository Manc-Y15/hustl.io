# Generated by Django 3.2.5 on 2022-03-01 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20220224_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='display_colour',
            field=models.TextField(blank=True, null=True),
        ),
    ]
