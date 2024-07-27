from django.db import models

from django.urls import reverse

from django.template.defaultfilters import slugify

from django.utils import timezone

from django.conf import settings
from os.path import join


class Evento(models.Model):
    CATEGORY_CHOICES = [('Concerti', 'Concerti'), ('Festival', 'Festival'), ('Teatro', 'Teatro')]
        
    nome = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=200, null=False,  blank=True, unique=True)
    categoria = models.CharField(max_length=100, choices=CATEGORY_CHOICES, null=False, blank=False)
    data_ora = models.DateTimeField(null=False, blank=False, default=timezone.now)
    locandina = models.ImageField(null=True, blank=True, upload_to="images/events")
    descrizione = models.TextField(null=True, blank=True, default='')
    visualizzazioni = models.IntegerField(null=True, blank=True, default=0)

    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=False, blank=False, related_name='eventi_organizzati')
    luogo = models.ForeignKey(to='common.Luogo', on_delete=models.CASCADE, null=False, blank=False, related_name='eventi_programmati')
    followers = models.ManyToManyField(to='users.Utente', blank=True, default=None, related_name='eventi_preferiti')
    

    def __str__(self):
        return f"{self.nome} - {self.organizzatore}"
    
    # django tratta il valore di default di un ImageField come un file media, cercandolo nella directory MEDIA_ROOT
    @property # trasforma un metodo di una classe in un attributo di sola lettura
    def locandina_url(self):
        if self.locandina and hasattr(self.locandina, 'url'):
            return self.locandina.url
        else:
            return join(settings.STATIC_URL, 'images/defaults/default_event.jpg')

    # restituisce l'URL assoluto per la visualizzazione dettagliata di un Evento
    def get_absolute_url(self):
        return reverse("products:event-details", kwargs={"slug": self.slug, "pk": self.pk})
    
    # lo slug viene aggiornato alla creazione di un Evento e ad ogni modifica del suo nome
    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.nome) != self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Eventi'


class Biglietto(models.Model):
    tipologia = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=200, null=False, blank=True)
    prezzo = models.FloatField(null=False, blank=False, default=0.00)
    quantita = models.IntegerField(null=False, blank=False, default=0)
    quantita_vendibile = models.IntegerField(null=False, blank=False, default=0)
    descrizione = models.TextField(null=True, blank=True, default='')
    
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_disponibili')
    organizzatore = models.ForeignKey(to='users.Organizzatore', on_delete=models.CASCADE, null=True, blank=True, related_name='biglietti_generati')


    def __str__(self):
        return f"{self.tipologia} - {self.evento}"

    # restituisce l'URL assoluto per la visualizzazione dettagliata del Luogo associato al Biglietto
    def get_absolute_url(self):
        return self.evento.get_absolute_url()
    
    # lo slug viene aggiornato alla creazione di un Biglietto e ad ogni modifica della sua tipologia
    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.tipologia) != self.slug:
            self.slug = slugify(self.tipologia)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Biglietti'