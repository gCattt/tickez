from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset

from products.models import Evento, Biglietto

import os


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
        super(EventCrispyForm, self).__init__(*args, **kwargs)
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
            'remove_locandina'
            'descrizione'
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get('remove_locandina'):
            if instance.locandina:
                try:
                    os.unlink(instance.locandina.path)
                except OSError:
                    pass
            instance.locandina = None

        if commit:
            instance.save()

        return instance
    

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
            'tipologia': forms.TextInput(attrs={'pattern': '^[A-Za-zÀ-ÿ ]{1,100}$'}),
            'prezzo': forms.NumberInput(attrs={'step': '0.01'}),
        }


    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'Crea Biglietto')
        super(TicketCrispyForm, self).__init__(*args, **kwargs)
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