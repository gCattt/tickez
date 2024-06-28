from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Evento

class EventCrispyForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ('organizzatore', 'categoria', 'nome', 'luogo', 'data_ora', 'descrizione')

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'Crea Evento')
        super(EventCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'event-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', action, css_class="btn-dark"))