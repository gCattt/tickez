# Generated by Django 5.0.6 on 2024-05-16 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifica',
            name='data_ora',
            field=models.DateTimeField(default='16/05/2024 22:23:16'),
        ),
    ]
