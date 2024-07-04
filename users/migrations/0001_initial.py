# Generated by Django 5.0.6 on 2024-07-04 15:52

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Utente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('cognome', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('data_nascita', models.DateField(blank=True, default=datetime.date.today, null=True)),
                ('sesso', models.CharField(blank=True, choices=[('M', 'Maschio'), ('F', 'Femmina'), ('Altro', 'Altro')], default='Altro', max_length=10, null=True)),
                ('stato', models.CharField(max_length=100)),
                ('indirizzo', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('telefono', models.CharField(blank=True, default=None, max_length=20, null=True)),
                ('carta_credito', models.CharField(blank=True, default=None, max_length=16, null=True)),
                ('cvv', models.CharField(blank=True, default=None, max_length=3, null=True)),
                ('scadenza_carta', models.DateField(blank=True, default=datetime.date.today, null=True)),
                ('notifiche', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Utenti',
            },
        ),
        migrations.CreateModel(
            name='Organizzatore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('descrizione', models.TextField(blank=True, default='', null=True)),
                ('notifiche', models.BooleanField(default=False)),
                ('followers', models.ManyToManyField(blank=True, default=None, related_name='organizzatori_preferiti', to='users.utente')),
            ],
            options={
                'verbose_name_plural': 'Organizzatori',
            },
        ),
    ]
