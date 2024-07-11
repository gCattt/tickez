from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset

from django.contrib.auth.models import User
from users.models import Utente

import os


class CustomerEditCrispyForm(forms.ModelForm):
    # campo aggiuntivo del modello User
    username = forms.CharField(
        max_length=150,
        help_text="Richiesto. Massimo 150 caratteri. Sono consentite lettere, cifre e @/./+/-/_.",
        widget=forms.TextInput(attrs={'pattern': '[A-Za-zÀ-ÿ0-9.@+-]+'}),
    )

    # aggiorna immagine_profilo senza mostrare il percorso del file attualmente caricato
    immagine_profilo = forms.ImageField(label=('Aggiorna immagine profilo'), widget=forms.FileInput, required=False)
    remove_immagine_profilo = forms.BooleanField(label=('Rimuovi immagine profilo'), required=False)

    class Meta:
        model = Utente
        fields = (  
            'username', 'email',
            'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'telefono', 'immagine_profilo', 'remove_immagine_profilo'
        )
        labels = {
            'email': 'Indirizzo email',
            'data_nascita': 'Data di nascita',
            'stato': 'Cittadinanza',
            'telefono': 'Numero di cellulare'
        }
        widgets = {
            'email': forms.EmailInput(attrs={'maxlength': 255}),
            'nome': forms.TextInput(attrs={'maxlength': 50, 'pattern': '[A-Za-zÀ-ÿ -]{1,50}'}),
            'cognome': forms.TextInput(attrs={'maxlength': 50, 'pattern': '[A-Za-zÀ-ÿ -]{1,50}'}),
            'data_nascita': forms.DateInput(attrs={'type': 'date'}),
            'telefono': forms.TextInput(attrs={'type': 'tel', 'pattern': '[0-9]{7,20}'}),
        }


    def __init__(self, *args, **kwargs):
        super(CustomerEditCrispyForm, self).__init__(*args, **kwargs)

        self.initial['username'] = self.instance.user.username

        self.helper = FormHelper()
        self.helper.form_id = 'customer-edit-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Salva modifiche', css_class="btn btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn btn-secondary mt-3"))

        self.helper.layout = Layout(
            Row(
                Column('nome', css_class='form-group col-md-6 mb-0'),
                Column('cognome', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('data_nascita', css_class='form-group col-md-4 mb-0'),
                Column('sesso', css_class='form-group col-md-4 mb-0'),
                Column('stato', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'username',
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('telefono', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'immagine_profilo',
            'remove_immagine_profilo'
        )

    def clean_username(self):
        new_username = self.cleaned_data['username']
        current_username = self.instance.user.username

        if new_username != current_username and User.objects.filter(username=new_username).exists():
            raise forms.ValidationError("Username già in uso.")

        return new_username

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        instance.user.username = self.cleaned_data['username']

        if self.cleaned_data.get('remove_immagine_profilo'):
            if instance.immagine_profilo:
                try:
                    os.unlink(instance.immagine_profilo.path)
                except OSError:
                    pass
            instance.immagine_profilo = None

        if commit:
            instance.user.save()
            instance.save()

        return instance