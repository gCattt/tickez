from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from datetime import datetime

class Evento(models.Model):
    
    CATEGORY_CHOICES = [
        ('Concerti', 'Concerti'),
        ('Festival', 'Festival'),
        ('Teatro', 'Teatro')
    ]
        
    nome = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=200, null=False, unique=True, blank=True)
    categoria = models.CharField(max_length=100, choices=CATEGORY_CHOICES, null=False, blank=False)
    descrizione = models.TextField(null=True, blank=True, default='')
    data_ora = models.DateTimeField(null=False, blank=False, default=datetime.now())
    # locandina = models.

    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=False, blank=False, related_name='eventi_organizzati')
    luogo = models.ForeignKey(to='common.Luogo', on_delete=models.CASCADE, null=False, blank=False, related_name='eventi_programmati')
    followers = models.ManyToManyField(to='users.Utente', blank=True, default=None, related_name='eventi_preferiti')
    
    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("products:event-details", kwargs={"slug": self.slug, "pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.nome) != self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Eventi'

class Biglietto(models.Model):
    tipologia = models.CharField(max_length=100, null=True, blank=True, default='')
    slug = models.SlugField(max_length=200, null=False, unique=True, blank=True)
    prezzo = models.FloatField(null=True, blank=True, default=0.00)
    descrizione = models.TextField(null=True, blank=True, default='')
    quantita = models.IntegerField(default=0)
    
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_generati')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_disponibili')
    ordine = models.ManyToManyField(to='orders.Ordine', blank=True, default=None, related_name='biglietti_ordinati')

    # def __str__(self):

    def get_absolute_url(self):
        return self.evento.get_absolute_url()
    
    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.tipologia) != self.slug:
            self.slug = slugify(self.tipologia)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Biglietti'