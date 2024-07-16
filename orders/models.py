from django.db import models

from django.utils import timezone
from datetime import timedelta


class Ordine(models.Model):
    data_ora = models.DateTimeField(null=False, blank=False, default=timezone.now)
    totale = models.FloatField(null=False, blank=False, default=0.00)
    
    utente = models.ForeignKey(to='users.Utente', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.PROTECT, null=False, blank=False, related_name="ordini")


    def __str__(self):
        return f"Ordine N. {self.pk} - {self.utente.nome} {self.utente.cognome}, {self.utente.email}"

    class Meta:
        verbose_name_plural = 'Ordini'
        

class BigliettoAcquistato(models.Model):
    GENDER_CHOICES = [('Altro', 'Altro'), ('Maschio', 'Maschio'), ('Femmina', 'Femmina')]
    
    nome_acquirente = models.CharField(max_length=50, null=False, blank=False)
    cognome_acquirente = models.CharField(max_length=50, null=False, blank=False)
    data_acquisto = models.DateTimeField(null=False, blank=False, default=timezone.now)
    data_nascita_acquirente = models.DateField(null=False, blank=False, default=timezone.now)
    sesso_acquirente = models.CharField(max_length=10, choices=GENDER_CHOICES, null=False, blank=False, default='Altro')
    stato_acquirente = models.CharField(max_length=50, null=False, blank=False)

    biglietto = models.ForeignKey(to='products.Biglietto', on_delete=models.CASCADE, null=False, blank=False, related_name='biglietti_acquistati')
    ordine = models.ForeignKey(Ordine, on_delete=models.CASCADE, null=False, blank=False, related_name='biglietti_acquistati')
    

    def __str__(self):
        return f'{self.biglietto.tipologia} - {self.nome_acquirente} {self.cognome_acquirente}, {self.data_acquisto}'
    
    def can_edit(self):
        return timezone.now() <= (self.biglietto.evento.data_ora - timedelta(days=15))
    
    class Meta:
        verbose_name_plural = 'Biglietti Acquistati'