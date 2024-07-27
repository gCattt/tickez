from django.db import models
from django.contrib.auth.models import User

from django.urls import reverse

from django.template.defaultfilters import slugify

from django.utils import timezone

from django.conf import settings
from os.path import join


class Utente(models.Model):
    GENDER_CHOICES = [('Altro', 'Altro'), ('Maschio', 'Maschio'), ('Femmina', 'Femmina')]

    nome = models.CharField(max_length=50, null=False, blank=False)
    cognome = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True)
    data_nascita = models.DateField(null=False, blank=False, default=timezone.now)
    sesso = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, default='Altro')
    stato = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True, default=None)
    immagine_profilo = models.ImageField(null=True, blank=True, upload_to="images/customers")

    '''
    l'eliminazione non è bidirezionale per impostazione predefinita per motivi di sicurezza e integrità dei dati.
    l'oggetto User, quindi, persiste anche se l'oggetto Utente viene eliminato
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.nome} {self.cognome} - {self.user.username}"
    
    # sincronizzazione tra i campi nome, cognome ed email delle tabelle users_utente e auth_user
    def save(self, *args, **kwargs):
        self.user.first_name = self.nome
        self.user.last_name = self.cognome
        self.user.email = self.email
        self.user.save()
        super(Utente, self).save(*args, **kwargs)
    
    # django tratta il valore di default di un ImageField come un file media, cercandolo nella directory MEDIA_ROOT
    @property # trasforma un metodo di una classe in un attributo di sola lettura
    def immagine_profilo_url(self):
        if self.immagine_profilo and hasattr(self.immagine_profilo, 'url'):
            return self.immagine_profilo.url
        else:
            return join(settings.STATIC_URL, 'images/defaults/default_user.jpg')

    class Meta:
        verbose_name_plural = 'Utenti'


class Organizzatore(models.Model):
    nome = models.CharField(max_length=50, null=False, blank=False)
    slug = models.SlugField(max_length=100, null=False, blank=True, unique=True)
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True)
    descrizione = models.TextField(null=True, blank=True, default='')
    immagine_profilo = models.ImageField(null=True, blank=True, upload_to="images/organizers")

    '''
    l'eliminazione non è bidirezionale per impostazione predefinita per motivi di sicurezza e integrità dei dati.
    l'oggetto User, quindi, persiste anche se l'oggetto Organizzatore viene eliminato
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(Utente, blank=True, default=None, related_name='organizzatori_preferiti')


    def __str__(self):
        return self.nome
    
    # restituisce l'URL assoluto per la visualizzazione dettagliata di un Organizzatore
    def get_absolute_url(self):
        return reverse("users:artist-details", kwargs={"slug": self.slug, "pk": self.pk})
    
    def save(self, *args, **kwargs):
        # sincronizzazione dell'email tra users_utente e auth_user
        self.user.email = self.email
        self.user.save()
        
        # lo slug viene aggiornato alla creazione di un Organizzatore e ad ogni modifica del suo nome
        if not self.slug or slugify(self.nome) != self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    # django tratta il valore di default di un ImageField come un file media, cercandolo nella directory MEDIA_ROOT
    @property # trasforma un metodo di una classe in un attributo di sola lettura
    def immagine_profilo_url(self):
        if self.immagine_profilo and hasattr(self.immagine_profilo, 'url'):
            return self.immagine_profilo.url
        else:
            return join(settings.STATIC_URL, 'images/defaults/default_user.jpg')

    class Meta:
        verbose_name_plural = 'Organizzatori'