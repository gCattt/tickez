# Generated by Django 5.0.6 on 2024-06-12 19:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0002_alter_notifica_data_ora'),
        ('orders', '0003_alter_ordine_data_ora'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('descrizione', models.TextField(blank=True, default='', null=True)),
                ('data_ora', models.DateTimeField(default='12/06/2024 21:17:46')),
                ('categoria', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('followers', models.ManyToManyField(blank=True, default=None, related_name='eventi_preferiti', to='users.utente')),
                ('luogo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eventi_programmati', to='common.luogo')),
                ('organizzatore', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eventi_organizzati', to='users.organizzatore')),
            ],
            options={
                'verbose_name_plural': 'Eventi',
            },
        ),
        migrations.CreateModel(
            name='Biglietto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipologia', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('prezzo', models.FloatField(blank=True, default=0.0, null=True)),
                ('descrizione', models.TextField(blank=True, default='', null=True)),
                ('ordine', models.ManyToManyField(blank=True, default=None, related_name='biglietti_ordinati', to='orders.ordine')),
                ('organizzatore', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='biglietti_generati', to='users.organizzatore')),
                ('evento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='biglietti_disponibili', to='products.evento')),
            ],
            options={
                'verbose_name_plural': 'Biglietti',
            },
        ),
    ]
