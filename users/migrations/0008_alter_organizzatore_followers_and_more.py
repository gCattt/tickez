# Generated by Django 5.0.6 on 2024-07-15 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_utente_carta_credito_remove_utente_cvv_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizzatore',
            name='followers',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='organizzatori_preferiti', to='users.utente'),
        ),
        migrations.AlterField(
            model_name='organizzatore',
            name='immagine_profilo',
            field=models.ImageField(blank=True, null=True, upload_to='images/organizers'),
        ),
        migrations.AlterField(
            model_name='utente',
            name='immagine_profilo',
            field=models.ImageField(blank=True, null=True, upload_to='images/customers'),
        ),
    ]
