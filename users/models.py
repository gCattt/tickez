from django.db import models
from django.contrib.auth.models import AbstractUser

from django.urls import reverse

from django.template.defaultfilters import slugify

from datetime import date


class Utente(AbstractUser):
        
    GENDER_CHOICES = [
        ('M', 'Maschio'),
        ('F', 'Femmina'),
        ('Altro', 'Altro')
    ]

    nome = models.CharField(max_length=100, null=False, blank=False)
    cognome = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False, unique=True)
    
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

    # sincronizzazione tra Utente.nome-User.first_name e tra Utente.cognome-User.last_name
    def save(self, *args, **kwargs):
        self.first_name = self.nome
        self.last_name = self.cognome
        super(Utente, self).save(*args, **kwargs)
    
    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Utenti'

class Organizzatore(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=200, null=False, unique=True, blank=True)
    descrizione = models.TextField(null=True, blank=True, default='')
    # immagine_profilo = models.
    notifiche = models.BooleanField(null=False, default=False)

    followers = models.ManyToManyField(Utente, blank=True, default=None, related_name='organizzatori_preferiti')

    def __str__(self):
        return self.nome
    
    def get_absolute_url(self):
        return reverse("users:artist_details", kwargs={"slug": self.slug, "pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Organizzatori'