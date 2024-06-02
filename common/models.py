from django.db import models
from datetime import datetime

class Luogo(models.Model):
    nome = models.CharField(max_length=50, null=False, blank=False)
    indirizzo = models.CharField(max_length=255)
    capienza_persone = models.PositiveIntegerField()
    citta = models.CharField(max_length=100)
    stato = models.CharField(max_length=100)
    codice_postale = models.CharField(max_length=30)
    # preview = models.

    followers = models.ManyToManyField(to='users.Utente', blank=True, default=None, related_name='luoghi_preferiti')
    affittuari = models.ManyToManyField(to='users.Organizzatore', blank=True, default=None, related_name='luoghi_affittati')
    
    #def __str__(self):
    
    class Meta:
        verbose_name_plural = 'Luoghi'

class Notifica(models.Model):
    testo = models.CharField(max_length=50, null=False, blank=False)
    data_ora = models.DateTimeField(null=False, blank=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    ordine = models.ForeignKey(to='orders.Ordine', on_delete=models.CASCADE, null=True, blank=True, related_name='notifiche_ordine')
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=True, blank=True, related_name='notifiche_organizzatore')
    luogo = models.ForeignKey(Luogo, on_delete=models.CASCADE, null=True, blank=True, related_name='notifiche_luogo')
    
    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Notifiche'