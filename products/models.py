from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from datetime import datetime

class Evento(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=200, null=False, unique=True, blank=True)
    descrizione = models.TextField(null=True, blank=True, default='')
    data_ora = models.DateTimeField(null=False, blank=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    categoria = models.CharField(max_length=100, null=True, blank=True, default='')
    # locandina = models.

    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=True, blank=True, related_name='eventi_organizzati')
    luogo = models.ForeignKey(to='common.Luogo', on_delete=models.CASCADE, null=True, blank=True, related_name='eventi_programmati')
    followers = models.ManyToManyField(to='users.Utente', blank=True, default=None, related_name='eventi_preferiti')
    
    # def __str__(self):

    def get_absolute_url(self):
        return reverse("products:event_details", kwargs={"slug": self.slug, "pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Eventi'

class Biglietto(models.Model):
    tipologia = models.CharField(max_length=100, null=True, blank=True, default='')
    prezzo = models.FloatField(null=True, blank=True, default=0.00)
    descrizione = models.TextField(null=True, blank=True, default='')
    
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_generati')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_disponibili')
    ordine = models.ManyToManyField(to='orders.Ordine', blank=True, default=None, related_name='biglietti_ordinati')

    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Biglietti'