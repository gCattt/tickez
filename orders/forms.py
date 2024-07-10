from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from .models import BigliettoAcquistato


class CheckoutCrispyForm(forms.Form):
    numero_carta = forms.CharField(max_length=16, label='Numero Carta')
    scadenza_carta = forms.DateField(
        widget=forms.DateInput(format='%m/%y'),
        input_formats=['%m/%y'],
        label='Scadenza Carta'
    )
    cvv = forms.CharField(max_length=3, label='CVV')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'checkout-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Paga ora', css_class="btn btn-success"))

class BigliettoAcquistatoCrispyForm(forms.ModelForm):
    class Meta:
        model = BigliettoAcquistato
        fields = ('nome_acquirente', 'cognome_acquirente')

    def __init__(self, *args, **kwargs):
        super(BigliettoAcquistatoCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'biglietto-acquistato-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Aggiorna', css_class="btn-dark"))