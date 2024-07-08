from django.db import models
from django.utils import timezone

class Ordine(models.Model):
    data_ora = models.DateTimeField(null=False, blank=False, default=timezone.now)
    totale = models.FloatField(null=False, blank=False, default=0.00)
    
    utente = models.ForeignKey(to='users.Utente', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")
    biglietti = models.ManyToManyField(to='products.Biglietto', blank=False, related_name="ordini")

    def __str__(self):
        return f"Ordine N. {self.pk} - {self.utente.nome} {self.utente.cognome}, {self.utente.email}"

    class Meta:
        verbose_name_plural = 'Ordini'