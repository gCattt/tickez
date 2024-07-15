from django import forms
from django.contrib.auth.forms import UserCreationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset

from django.contrib.auth.models import User, Group
from users.models import Utente, Organizzatore

import os


class CustomerCreationForm(UserCreationForm):
    # campi aggiuntivi del modello Utente
    nome = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'pattern': '^[A-Za-zÀ-ÿ -]{1,50}$'})
    )
    cognome = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'pattern': '^[A-Za-zÀ-ÿ -]{1,50}$'})
    )
    email = forms.EmailField(label='Indirizzo email', max_length=255)
    data_nascita = forms.DateField(
        label='Data di nascita',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    sesso = forms.ChoiceField(choices=Utente.GENDER_CHOICES, required=False)
    stato = forms.CharField(
        label='Cittadinanza',
        max_length=50, 
        widget=forms.TextInput(attrs={'pattern': '^[A-Za-zÀ-ÿ -]{1,50}$'})
    )
    telefono = forms.CharField(
        label='Numero di cellulare',
        max_length=20, 
        widget=forms.TextInput(attrs={'type': 'tel', 'pattern': '[0-9]{7,20}'}),
        required=False
    )
    immagine_profilo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        # username, password1 e password2 possono essere inclusi anche tramite 'fields = UserCreationForm.Meta.fields + (...)'
        fields = (  
            'username', 'email', 'password1', 'password2',
            'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'telefono', 'immagine_profilo'
        )


    def __init__(self, *args, **kwargs):
        super(CustomerCreationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'customer-creation-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Crea Account', css_class="btn btn-dark mt-3"))
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
            'password1',
            'password2',
            'immagine_profilo',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            u = Utente(
                user=user,
                immagine_profilo=self.cleaned_data['immagine_profilo'],
                nome=self.cleaned_data['nome'],
                cognome=self.cleaned_data['cognome'],
                email=self.cleaned_data['email'],
                data_nascita=self.cleaned_data['data_nascita'],
                sesso=self.cleaned_data['sesso'],
                stato=self.cleaned_data['stato'],
                telefono=self.cleaned_data['telefono'],
            )
            u.save()
            group = Group.objects.get(name="Clienti")
            # la gestione dei gruppi e delle autorizzazioni in Django è strettamente legata al modello User
            user.groups.add(group)
        return user


class OrganizerCreationForm(UserCreationForm):
    # campi aggiuntivi del modello Organizzatore
    nome = forms.CharField(
        label='Nome organizzatore',
        max_length=50,
        widget=forms.TextInput(attrs={'pattern': '^[A-Za-zÀ-ÿ -]{1,50}$'})
    )
    email = forms.EmailField(
        label='Indirizzo email',
        max_length=255,
    )
    descrizione = forms.CharField(widget=forms.Textarea, required=False)
    immagine_profilo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        # username, password1 e password2 possono essere inclusi anche tramite 'fields = UserCreationForm.Meta.fields + (...)'
        fields = (
            'username', 'email', 'password1', 'password2', 
            'nome', 'descrizione', 'immagine_profilo'
        )

    
    def __init__(self, *args, **kwargs):
        super(OrganizerCreationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'organizer-creation-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Crea Account', css_class="btn btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn btn-secondary mt-3"))

        self.helper.layout = Layout(
            'username',
            'email',
            'password1',
            'password2',
            'nome', 
            'descrizione',
            'immagine_profilo',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            o = Organizzatore(
                user=user,
                immagine_profilo=self.cleaned_data['immagine_profilo'],
                nome=self.cleaned_data['nome'],
                email=self.cleaned_data['email'],
                descrizione=self.cleaned_data['descrizione'],
            )
            o.save()
            group = Group.objects.get(name="Organizzatori")
            # la gestione dei gruppi e delle autorizzazioni in Django è strettamente legata al modello User
            user.groups.add(group)
        return user


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
    
class OrganizzatoreEditCrispyForm(forms.ModelForm):
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
        model = Organizzatore
        fields = ('username', 'email', 'nome', 'descrizione', 'immagine_profilo', 'remove_immagine_profilo')
        labels = {
            'email': 'Indirizzo email',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'maxlength': 255}),
            'nome': forms.TextInput(attrs={'maxlength': 50, 'pattern': '[A-Za-zÀ-ÿ -]{1,50}'}),
        }

    def __init__(self, *args, **kwargs):
        super(OrganizzatoreEditCrispyForm, self).__init__(*args, **kwargs)

        self.initial['username'] = self.instance.user.username

        self.helper = FormHelper()
        self.helper.form_id = 'organizzatore-edit-crispy-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Salva modifiche', css_class="btn btn-dark mt-3"))
        self.helper.add_input(Reset('reset', 'Ripristina', css_class="btn btn-secondary mt-3"))

        self.helper.layout = Layout(
            'username',
            'email',
            'nome',
            'descrizione',
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