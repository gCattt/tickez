# Generated by Django 5.0.6 on 2024-06-04 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_notifica_data_ora'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifica',
            name='data_ora',
            field=models.DateTimeField(default='05/06/2024 00:42:39'),
        ),
    ]
