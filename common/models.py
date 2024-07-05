from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.utils import timezone

class Luogo(models.Model):
    nome = models.CharField(max_length=50, null=False, blank=False)
    slug = models.SlugField(max_length=200, null=False, unique=True, blank=True)
    indirizzo = models.CharField(max_length=255)
    capienza_persone = models.PositiveIntegerField()
    citta = models.CharField(max_length=100)
    stato = models.CharField(max_length=100)
    codice_postale = models.CharField(max_length=30)
    # preview = models.

    followers = models.ManyToManyField(to='users.Utente', blank=True, default=None, related_name='luoghi_preferiti')
    affittuari = models.ManyToManyField(to='users.Organizzatore', blank=True, default=None, related_name='luoghi_affittati')
    
    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("common:venue-details", kwargs={"slug": self.slug, "pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Luoghi'

class Notifica(models.Model):
    testo = models.CharField(max_length=50, null=False, blank=False)
    data_ora = models.DateTimeField(null=False, blank=False, default=timezone.now)

    ordine = models.ForeignKey(to='orders.Ordine', on_delete=models.CASCADE, null=True, blank=True, related_name='notifiche_ordine')
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=True, blank=True, related_name='notifiche_organizzatore')
    luogo = models.ForeignKey(Luogo, on_delete=models.CASCADE, null=True, blank=True, related_name='notifiche_luogo')
    
    # def __str__(self):

    class Meta:
        verbose_name_plural = 'Notifiche'