# Generated by Django 5.0.6 on 2024-07-15 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_remove_biglietto_ordine_alter_biglietto_slug_and_more'),
        ('users', '0009_alter_organizzatore_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='followers',
            field=models.ManyToManyField(blank=True, default=None, related_name='eventi_preferiti', to='users.utente'),
        ),
    ]