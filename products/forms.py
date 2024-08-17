from django import forms

from django.shortcuts import get_object_or_404

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset

from products.models import Evento, Biglietto
from users.models import Organizzatore
from django.db.models import Sum

import os

from django.utils import timezone

# creazione/modifica di eventi da parte dell'admin (aggiunge il campo organizzatore)
class AdminEventCrispyForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ('organizzatore', 'categoria', 'nome', 'luogo', 'data_ora', 'descrizione', 'locandina')
        labels = {
            'nome': 'Nome dell\'evento',
            'data_ora': 'Data e Ora',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'maxlength': 100}),
            'data_ora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'locandina': forms.ClearableFileInput(),
        }


    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'Crea Evento')
        super(AdminEventCrispyForm, self).__init__(*args, **kwargs)

        self.initial['data_ora'] = self.instance.data_ora.strftime('%Y-%m-%dT%H:%M')

        # la classe FormHelper offre un modo semplice per gestire il layout e lo stile degli elementi di un form
        self.helper = FormHelper()
        self.helper.form_id = 'event-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', action, css_class="btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn-secondary mt-3"))

        self.helper.layout = Layout(
            'organizzatore',
            'nome',
            'luogo',
            Row(
                Column('categoria', css_class='form-group col-md-6 mb-0'),
                Column('data_ora', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'locandina',
            'descrizione'
        )

    # validazione lato server:
    def clean_nome(self):
        nome = self.cleaned_data['nome']
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # modifica (devo escludere l'istanza del modello considerata)
            if Evento.objects.exclude(pk=instance.pk).filter(nome=nome).exists():
                raise forms.ValidationError("Questo nome evento è già utilizzato.")
        else:
            # creazione
            if Evento.objects.filter(nome=nome).exists():
                raise forms.ValidationError("Questo nome evento è già utilizzato.")
        return nome

    def clean_data_ora(self):
        data_ora = self.cleaned_data['data_ora']
        instance = getattr(self, 'instance', None)
        
        if data_ora < timezone.now():
            raise forms.ValidationError("La data e l'ora dell'evento non possono essere nel passato.")
        
        # evita sovrapposizioni per lo stesso organizzatore
        organizzatore = self.cleaned_data.get('organizzatore')
        if organizzatore:
            eventi_stesso_giorno = Evento.objects.filter(
                organizzatore=organizzatore,
                data_ora__date=data_ora.date()
            )
            if instance and instance.pk:
                eventi_stesso_giorno = eventi_stesso_giorno.exclude(pk=instance.pk)
            if eventi_stesso_giorno.exists():
                raise forms.ValidationError("L'organizzatore ha già un altro evento programmato in questa data.")

        # evita sovrapposizioni nello stesso luogo
        luogo = self.cleaned_data.get('luogo')
        if luogo:
            eventi_stesso_luogo = Evento.objects.filter(
                luogo=luogo,
                data_ora__date=data_ora.date()
            )
            if instance and instance.pk:
                eventi_stesso_luogo = eventi_stesso_luogo.exclude(pk=instance.pk)
            if eventi_stesso_luogo.exists():
                raise forms.ValidationError("Questo luogo ha già un altro evento programmato in questa data.")
            
        return data_ora

    def clean_locandina(self):
        locandina = self.cleaned_data['locandina']
        if locandina:
            # verifica l'estensione del file
            file_name, file_extension = os.path.splitext(locandina.name)
            if file_extension.lower() not in ['.png', '.jpeg', '.jpg']:
                raise forms.ValidationError("L'estensione del file non è supportata. Utilizza file .png, .jpeg o .jpg.")
        return locandina


# creazione/modifica di eventi da parte di un Organizzatore
class EventCrispyForm(forms.ModelForm):
    # aggiorna locandina senza mostrare il percorso del file attualmente caricato
    locandina = forms.ImageField(label=('Aggiorna locandina'), required=False, widget=forms.FileInput)
    remove_locandina = forms.BooleanField(label=('Rimuovi locandina'), required=False)

    class Meta:
        model = Evento
        fields = ('categoria', 'nome', 'luogo', 'data_ora', 'descrizione', 'locandina', 'remove_locandina')
        labels = {
            'nome': 'Nome dell\'evento',
            'data_ora': 'Data e Ora',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'maxlength': 100}),
            'data_ora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'Crea Evento')
        self.user = kwargs.pop('user', None) 
        super(EventCrispyForm, self).__init__(*args, **kwargs)

        self.initial['data_ora'] = self.instance.data_ora.strftime('%Y-%m-%dT%H:%M')

        # la classe FormHelper offre un modo semplice per gestire il layout e lo stile degli elementi di un form
        self.helper = FormHelper()
        self.helper.form_id = 'event-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', action, css_class="btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn-secondary mt-3"))

        self.helper.layout = Layout(
            'nome',
            'luogo',
            Row(
                Column('categoria', css_class='form-group col-md-6 mb-0'),
                Column('data_ora', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'locandina',
            'remove_locandina',
            'descrizione'
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get('remove_locandina'):
            # se esiste una locandina associata all'istanza, la si rimuove dal file system del server e si setta il campo nel db a None
            if instance.locandina:
                try:
                    os.unlink(instance.locandina.path)
                except OSError:
                    pass
            instance.locandina = None

        if commit:
            instance.save()

        return instance
    
    # validazione lato server:
    def clean_nome(self):
        nome = self.cleaned_data['nome']
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # modifica (devo escludere l'istanza del modello considerata)
            if Evento.objects.exclude(pk=instance.pk).filter(nome=nome).exists():
                raise forms.ValidationError("Questo nome evento è già utilizzato.")
        else:
            # creazione
            if Evento.objects.filter(nome=nome).exists():
                raise forms.ValidationError("Questo nome evento è già utilizzato.")
        return nome

    def clean_data_ora(self):
        data_ora = self.cleaned_data['data_ora']
        instance = getattr(self, 'instance', None)
        
        if data_ora < timezone.now():
            raise forms.ValidationError("La data e l'ora dell'evento non possono essere nel passato.")
        
        # evita sovrapposizioni per lo stesso organizzatore
        organizzatore = get_object_or_404(Organizzatore, user=self.user)
        if organizzatore:
            eventi_stesso_giorno = Evento.objects.filter(
                organizzatore=organizzatore,
                data_ora__date=data_ora.date()
            )
            if instance and instance.pk:
                eventi_stesso_giorno = eventi_stesso_giorno.exclude(pk=instance.pk)
            if eventi_stesso_giorno.exists():
                raise forms.ValidationError("L'organizzatore ha già un altro evento programmato in questa data.")

        # evita sovrapposizioni nello stesso luogo
        luogo = self.cleaned_data.get('luogo')
        if luogo:
            eventi_stesso_luogo = Evento.objects.filter(
                luogo=luogo,
                data_ora__date=data_ora.date()
            )
            if instance and instance.pk:
                eventi_stesso_luogo = eventi_stesso_luogo.exclude(pk=instance.pk)
            if eventi_stesso_luogo.exists():
                raise forms.ValidationError("Questo luogo ha già un altro evento programmato in questa data.")

        return data_ora

    def clean_locandina(self):
        locandina = self.cleaned_data['locandina']
        if locandina:
            # verifica l'estensione del file
            file_name, file_extension = os.path.splitext(locandina.name)
            if file_extension.lower() not in ['.png', '.jpeg', '.jpg']:
                raise forms.ValidationError("L'estensione del file non è supportata. Utilizza file .png, .jpeg o .jpg.")
        return locandina
    

# creazione/modifica di tipologie di biglietti associate agli eventi
class TicketCrispyForm(forms.ModelForm):
    class Meta:
        model = Biglietto
        fields = ('tipologia', 'prezzo', 'quantita', 'descrizione')
        labels = {
            'tipologia': 'Tipologia di biglietto',
            'prezzo': 'Prezzo (EUR)',
            'quantita': 'Quantità disponibile',
            'descrizione': 'Descrizione del biglietto',
        }
        widgets = {
            'tipologia': forms.TextInput(attrs={'pattern': '^[A-Za-zÀ-ÿ0-9.@+- ]{1,100}$'}),
            'prezzo': forms.NumberInput(attrs={'step': '0.01'}),
        }


    def __init__(self, *args, **kwargs):
        self.evento = kwargs.pop('evento', None)
        action = kwargs.pop('action', 'Crea Biglietto')
        super(TicketCrispyForm, self).__init__(*args, **kwargs)

        # la classe FormHelper offre un modo semplice per gestire il layout e lo stile degli elementi di un form
        self.helper = FormHelper()
        self.helper.form_id = 'ticket-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', action, css_class="btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn-secondary mt-3"))

        self.helper.layout = Layout(
            'tipologia',
            Row(
                Column('prezzo', css_class='form-group col-md-6 mb-0'),
                Column('quantita', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'descrizione'
        )

    # validazione lato server:
    def clean_prezzo(self):
        prezzo = self.cleaned_data['prezzo']
        if prezzo <= 0:
            raise forms.ValidationError("Il prezzo deve essere maggiore di zero.")
        return prezzo

    def clean_quantita(self):
        quantita = self.cleaned_data['quantita']
        if quantita < 0:
            raise forms.ValidationError("La quantità disponibile non può essere negativa.")
        if self.evento:
            # valida la quantità in relazione alla capienza del luogo dell'evento
            capienza = self.evento.luogo.capienza_persone

            # calcola la quantità totale dei biglietti escludendo il biglietto attualmente in modifica
            biglietti_esistenti = Biglietto.objects.filter(evento=self.evento).exclude(pk=self.instance.pk if self.instance else None).aggregate(total=Sum('quantita'))['total'] or 0
            if biglietti_esistenti + quantita > capienza:
                raise forms.ValidationError(f"La quantità totale dei biglietti supera la capienza del luogo ({biglietti_esistenti}/{capienza} biglietti già creati).")
        
        return quantita