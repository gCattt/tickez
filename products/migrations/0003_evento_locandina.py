# Generated by Django 5.0.6 on 2024-07-06 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_evento_categoria_alter_evento_data_ora'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='locandina',
            field=models.ImageField(blank=True, default='static\\images\\defaults\\default_event.png', upload_to='images/events'),
        ),
    ]