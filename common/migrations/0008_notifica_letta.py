# Generated by Django 5.0.6 on 2024-07-09 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_alter_luogo_immagine'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifica',
            name='letta',
            field=models.BooleanField(default=False),
        ),
    ]
