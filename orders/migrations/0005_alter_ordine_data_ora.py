# Generated by Django 5.0.6 on 2024-06-04 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_ordine_data_ora'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordine',
            name='data_ora',
            field=models.DateTimeField(default='05/06/2024 00:42:39'),
        ),
    ]