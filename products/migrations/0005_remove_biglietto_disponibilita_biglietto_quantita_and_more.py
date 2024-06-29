# Generated by Django 5.0.6 on 2024-06-29 08:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_biglietto_disponibilita_alter_evento_data_ora'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='biglietto',
            name='disponibilita',
        ),
        migrations.AddField(
            model_name='biglietto',
            name='quantita',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='evento',
            name='data_ora',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 29, 10, 29, 58, 503828)),
        ),
    ]
