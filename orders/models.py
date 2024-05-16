from django.db import models
from datetime import datetime
#from customers.models import Utente
#from sellers.models import Organizzatore, Biglietto

class Ordine(models.Model):
    data_ora = models.DateTimeField(null=False, blank=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    totale = models.FloatField(null=False, blank=False, default=0.00)
    
    utente = models.ForeignKey(to='customers.Utente', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")
    organizzatore = models.ForeignKey(to='sellers.Organizzatore', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")
    biglietti = models.ManyToManyField(to='sellers.Biglietto', blank=True, default=None, related_name='ordini')
    
    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Ordini'