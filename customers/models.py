from django.db import models
from datetime import date
#from common.models import Luogo
#from sellers.models import Organizzatore, Evento

class Utente(models.Model):
        
    GENDER_CHOICES = [
        ('M', 'Maschio'),
        ('F', 'Femmina'),
        ('Altro', 'Altro')
    ]

    nome = models.CharField(max_length=100, null=False, blank=False)
    cognome = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    
    data_nascita = models.DateField(null=True, blank=True, default=date.today)
    sesso = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, default='Altro')
    stato = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=50, null=True, blank=True, default=None)
    telefono = models.CharField(max_length=20, null=True, blank=True, default=None)
    # immagine_profilo = models.
    carta_credito = models.CharField(max_length=16, null=True, default=None, blank=True)
    cvv = models.CharField(max_length=3, null=True, blank=True, default=None)
    scadenza_carta = models.DateField(null=True, blank=True, default=date.today)
    notifiche = models.BooleanField(null=False, default=False)
    
    luoghi_preferiti = models.ManyToManyField(to='common.Luogo', blank=True, default=None, related_name='followers')
    organizzatori_preferiti = models.ManyToManyField(to='sellers.Organizzatore', blank=True, default=None, related_name='followers')
    eventi_preferiti = models.ManyToManyField(to='sellers.Evento', blank=True, default=None, related_name='followers')
    
    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Utenti'