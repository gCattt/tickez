# Generated by Django 5.0.6 on 2024-07-07 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_evento_locandina'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='locandina',
            field=models.ImageField(blank=True, default='images/defaults/default_event.jpg', upload_to='images/events'),
        ),
    ]
