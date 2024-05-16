from django.db import models
from datetime import datetime
#from common.models import Luogo

class Organizzatore(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    descrizione = models.TextField(null=True, blank=True, default='')
    # immagine_profilo = models.
    notifiche = models.BooleanField(null=False, default=False)

    luoghi_affittati = models.ManyToManyField(to='common.Luogo', blank=True, default=None, related_name='affittuari')

    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Organizzatori'

class Evento(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    descrizione = models.TextField(null=True, blank=True, default='')
    data_ora = models.DateTimeField(null=False, blank=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    categoria = models.CharField(max_length=100)
    # locandina = models.

    organizzatore = models.ForeignKey(Organizzatore, on_delete=models.CASCADE, null=True, blank=True, related_name='eventi_organizzati')
    luogo = models.ForeignKey(to='common.Luogo', on_delete=models.CASCADE, null=True, blank=True, related_name='eventi_programmati')
    
    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Eventi'

class Biglietto(models.Model):
    tipologia = models.CharField(max_length=100)
    prezzo = models.FloatField(null=False, blank=False, default=0.00)
    descrizione = models.TextField(null=True, blank=True, default='')
    
    organizzatore = models.ForeignKey(Organizzatore, on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_generati')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_disponibili')

    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Biglietti'