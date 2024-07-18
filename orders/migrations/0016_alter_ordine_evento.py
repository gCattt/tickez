# Generated by Django 5.0.6 on 2024-07-17 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_alter_ordine_evento'),
        ('products', '0011_biglietto_quantita_vendibile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordine',
            name='evento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordini', to='products.evento'),
        ),
    ]