# Generated by Django 5.0.6 on 2024-06-02 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='data_ora',
            field=models.DateTimeField(default='03/06/2024 00:22:14'),
        ),
    ]