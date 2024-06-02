from django.db import models
from datetime import datetime

class Ordine(models.Model):
    data_ora = models.DateTimeField(null=False, blank=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    totale = models.FloatField(null=False, blank=False, default=0.00)
    
    utente = models.ForeignKey(to='users.Utente', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")
    
    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Ordini'