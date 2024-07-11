from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Evento, Biglietto

import os


class AdminEventCrispyForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ('organizzatore', 'categoria', 'nome', 'luogo', 'data_ora', 'descrizione', 'locandina')

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'Crea Evento')
        super(AdminEventCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'event-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', action, css_class="btn-dark mt-3"))

class EventCrispyForm(forms.ModelForm):
    # aggiorna locandina senza mostrare il percorso del file attualmente caricato
    locandina = forms.ImageField(label=('Aggiorna locandina'), required=False, widget=forms.FileInput)
    remove_locandina = forms.BooleanField(label=('Rimuovi locandina'), required=False)

    class Meta:
        model = Evento
        fields = ('categoria', 'nome', 'luogo', 'data_ora', 'descrizione', 'locandina', 'remove_locandina')

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'Crea Evento')
        super(EventCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'event-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', action, css_class="btn-dark"))

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

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'Crea Biglietto')
        super(TicketCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'ticket-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', action, css_class="btn-dark"))