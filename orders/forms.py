from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset

from orders.models import BigliettoAcquistato

from django.utils import timezone


class CheckoutCrispyForm(forms.Form):
    titolare_carta = forms.CharField(
        max_length=100,
        label='Titolare carta',
        widget=forms.TextInput(attrs={'placeholder': 'Nome Cognome' ,'pattern': '^[A-Za-zÀ-ÿ -]{1,100}$'})
    )
    numero_carta = forms.CharField(
        max_length=16,
        label='Numero carta',
        widget=forms.TextInput(attrs={'placeholder': 'XXXX XXXX XXXX XXXX', 'pattern': '^([0-9]{4}[- ]?){3}[0-9]{4}$'})
    )
    scadenza_carta = forms.DateField(
        input_formats=['%m/%y'],
        label='Data di scadenza',
        widget=forms.DateInput(format='%m/%y', attrs={'placeholder': 'MM/YY', 'pattern': '^(0[1-9]|1[0-2])/[0-9]{2}$'})
    )
    cvv = forms.CharField(
        max_length=3,
        label='CVV',
        widget=forms.TextInput(attrs={'placeholder': 'XXX', 'pattern': '^[0-9]{3}$'})
    )


    def __init__(self, *args, **kwargs):
        super(CheckoutCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'checkout-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Paga', css_class="btn btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn btn-secondary mt-3"))

        self.helper.layout = Layout(
            'titolare_carta',
            'numero_carta',
            Row(
                Column('scadenza_carta', css_class='form-group col-md-6 mb-0'),
                Column('cvv', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
        )

    # validazione lato server
    def clean_titolare_carta(self):
        titolare_carta = self.cleaned_data['titolare_carta']
        if any(char.isdigit() for char in titolare_carta):
            raise forms.ValidationError("Il titolare della carta non può contenere numeri.")
        return titolare_carta
    
    def clean_numero_carta(self):
        numero_carta = self.cleaned_data['numero_carta']
        sanitized_number = numero_carta.replace(' ', '').replace('-', '')  # rimuovi spazi e trattini
        if not sanitized_number.isdigit():
            raise forms.ValidationError("Il numero della carta non è valido.")
        return numero_carta
    
    def clean_scadenza_carta(self):
        scadenza_carta = self.cleaned_data['scadenza_carta']
        if scadenza_carta < timezone.now().date():
            raise forms.ValidationError("La carta è scaduta.")
        return scadenza_carta
    
    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) != 3:
            raise forms.ValidationError("Il CVV deve essere un numero di 3 cifre.")
        return cvv


class BigliettoAcquistatoCrispyForm(forms.ModelForm):
    class Meta:
        model = BigliettoAcquistato
        fields = ('nome_acquirente', 'cognome_acquirente')
        labels = {
            'nome_acquirente': 'Nome',
            'cognome_acquirente': 'Cognome',
        }
        widgets = {
            'nome_acquirente': forms.TextInput(attrs={'maxlength': 50, 'pattern': '^[A-Za-zÀ-ÿ -]{1,50}$'}),
            'cognome_acquirente': forms.TextInput(attrs={'maxlength': 50, 'pattern': '^[A-Za-zÀ-ÿ -]{1,50}$'}),
        }


    def __init__(self, *args, **kwargs):
        super(BigliettoAcquistatoCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'biglietto-acquistato-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Aggiorna', css_class="btn btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn btn-secondary mt-3"))

        self.helper.layout = Layout(
            Row(
                Column('nome_acquirente', css_class='form-group col-md-6 mb-0'),
                Column('cognome_acquirente', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
        )

    # validazione lato server
    def clean_nome_acquirente(self):
        nome_acquirente = self.cleaned_data['nome_acquirente']
        if any(char.isdigit() for char in nome_acquirente):
            raise forms.ValidationError("Il nome non può contenere numeri.")
        return nome_acquirente

    def clean_cognome_acquirente(self):
        cognome_acquirente = self.cleaned_data['cognome_acquirente']
        if any(char.isdigit() for char in cognome_acquirente):
            raise forms.ValidationError("Il cognome non può contenere numeri.")
        return cognome_acquirente