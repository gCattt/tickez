# Generated by Django 5.0.6 on 2024-07-15 11:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_bigliettoacquistato_cognome_acquirente_and_more'),
        ('products', '0008_alter_biglietto_prezzo_alter_biglietto_tipologia_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bigliettoacquistato',
            name='biglietto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='biglietti_acquistati', to='products.biglietto'),
        ),
    ]
