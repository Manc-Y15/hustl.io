# Generated by Django 3.2.5 on 2022-03-02 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20220302_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='stock_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.stock'),
        ),
    ]
