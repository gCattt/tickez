# Generated by Django 5.0.6 on 2024-07-15 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_alter_luogo_affittuari_alter_luogo_followers_and_more'),
        ('users', '0009_alter_organizzatore_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='luogo',
            name='affittuari',
            field=models.ManyToManyField(blank=True, default=None, related_name='luoghi_affittati', to='users.organizzatore'),
        ),
        migrations.AlterField(
            model_name='luogo',
            name='followers',
            field=models.ManyToManyField(blank=True, default=None, related_name='luoghi_preferiti', to='users.utente'),
        ),
    ]