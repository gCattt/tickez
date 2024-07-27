from django import forms
from django.contrib.auth.forms import UserCreationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset

from django.contrib.auth.models import User, Group
from users.models import Utente, Organizzatore

import os

from django.utils import timezone


# creazione Utente
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

        # la classe FormHelper offre un modo semplice per gestire il layout e lo stile degli elementi di un form
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
        # creazione oggetto Utente ed associazione con il model User
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
    
    # validazione lato server
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(("Username già in uso."))
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(("Indirizzo email già in uso."))
        return email
    
    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if any(char.isdigit() for char in nome):
            raise forms.ValidationError("Il nome non può contenere numeri.")
        return nome

    def clean_cognome(self):
        cognome = self.cleaned_data['cognome']
        if any(char.isdigit() for char in cognome):
            raise forms.ValidationError("Il cognome non può contenere numeri.")
        return cognome

    def clean_data_nascita(self):
        data_nascita = self.cleaned_data.get('data_nascita')
        if data_nascita >= timezone.now().date():
            raise forms.ValidationError(("La data di nascita deve essere nel passato."))
        return data_nascita
    
    def clean_stato(self):
        stato = self.cleaned_data['stato']
        if any(char.isdigit() for char in stato):
            raise forms.ValidationError("La cittadinanza non può contenere numeri.")
        return stato

    def clean_immagine_profilo(self):
        immagine_profilo = self.cleaned_data.get('immagine_profilo')
        if immagine_profilo:
            # verifica l'estensione del file
            file_name, file_extension = os.path.splitext(immagine_profilo.name)
            if file_extension.lower() not in ['.png', '.jpeg', '.jpg']:
                raise forms.ValidationError("L'estensione del file non è supportata. Utilizza file .png, .jpeg o .jpg.")
        return immagine_profilo

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise forms.ValidationError("Il numero di telefono deve contenere solo cifre.")
        return telefono


# creazione Organizzatore
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

        # la classe FormHelper offre un modo semplice per gestire il layout e lo stile degli elementi di un form
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
        # creazione oggetto Organizzatore ed associazione con il model User
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
    
    # validazione lato server
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(("Username già in uso."))
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Indirizzo email già in uso.")
        return email

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if any(char.isdigit() for char in nome):
            raise forms.ValidationError("Il nome non può contenere numeri.")
        return nome

    def clean_immagine_profilo(self):
        immagine_profilo = self.cleaned_data.get('immagine_profilo')
        if immagine_profilo:
            # verifica l'estensione del file
            file_name, file_extension = os.path.splitext(immagine_profilo.name)
            if file_extension.lower() not in ['.png', '.jpeg', '.jpg']:
                raise forms.ValidationError("L'estensione del file non è supportata. Utilizza file .png, .jpeg o .jpg.")
        return immagine_profilo


# modifica Utente
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
            'data_nascita': forms.DateInput(attrs={'type': 'date-local'}),
            'sesso': forms.Select(attrs={'choices': Utente.GENDER_CHOICES}),
            'telefono': forms.TextInput(attrs={'type': 'tel', 'pattern': '[0-9]{7,20}'}),
        }


    def __init__(self, *args, **kwargs):
        super(CustomerEditCrispyForm, self).__init__(*args, **kwargs)

        self.initial['username'] = self.instance.user.username

        # la classe FormHelper offre un modo semplice per gestire il layout e lo stile degli elementi di un form
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # la modifica del model Utente si riflette sul model User
        instance.user.username = self.cleaned_data['username']

        if self.cleaned_data.get('remove_immagine_profilo'):
            # se esiste una immagine profilo associata all'istanza, la si rimuove dal file system del server e si setta il campo nel db a None
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
    
    # validazione lato server
    def clean_username(self):
        new_username = self.cleaned_data['username']
        current_username = self.instance.user.username

        if new_username != current_username and User.objects.filter(username=new_username).exists():
            raise forms.ValidationError("Username già in uso.")
        return new_username
    
    def clean_email(self):
        new_email = self.cleaned_data['email']
        current_email = self.instance.user.email

        if new_email != current_email and User.objects.filter(email=new_email).exists():
            raise forms.ValidationError("Indirizzo email già in uso.")
        return new_email
    
    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if any(char.isdigit() for char in nome):
            raise forms.ValidationError("Il nome non può contenere numeri.")
        return nome

    def clean_cognome(self):
        cognome = self.cleaned_data['cognome']
        if any(char.isdigit() for char in cognome):
            raise forms.ValidationError("Il cognome non può contenere numeri.")
        return cognome

    def clean_data_nascita(self):
        data_nascita = self.cleaned_data.get('data_nascita')
        if data_nascita >= timezone.now().date():
            raise forms.ValidationError(("La data di nascita deve essere nel passato."))
        return data_nascita
    
    def clean_stato(self):
        stato = self.cleaned_data['stato']
        if any(char.isdigit() for char in stato):
            raise forms.ValidationError("La cittadinanza non può contenere numeri.")
        return stato

    def clean_immagine_profilo(self):
        immagine_profilo = self.cleaned_data.get('immagine_profilo')
        if immagine_profilo:
            # verifica l'estensione del file
            file_name, file_extension = os.path.splitext(immagine_profilo.name)
            if file_extension.lower() not in ['.png', '.jpeg', '.jpg']:
                raise forms.ValidationError("L'estensione del file non è supportata. Utilizza file .png, .jpeg o .jpg.")
        return immagine_profilo

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise forms.ValidationError("Il numero di telefono deve contenere solo cifre.")
        return telefono


# modifica Organizzatore
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # la modifica del model Organizzatore si riflette sul model User
        instance.user.username = self.cleaned_data['username']

        if self.cleaned_data.get('remove_immagine_profilo'):
            # se esiste una immagine profilo associata all'istanza, la si rimuove dal file system del server e si setta il campo nel db a None
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
    
    # validazione lato server
    def clean_username(self):
        new_username = self.cleaned_data['username']
        current_username = self.instance.user.username

        if new_username != current_username and User.objects.filter(username=new_username).exists():
            raise forms.ValidationError("Username già in uso.")
        return new_username
    
    def clean_email(self):
        new_email = self.cleaned_data['email']
        current_email = self.instance.user.email

        if new_email != current_email and User.objects.filter(email=new_email).exists():
            raise forms.ValidationError("Indirizzo email già in uso.")
        return new_email

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if any(char.isdigit() for char in nome):
            raise forms.ValidationError("Il nome non può contenere numeri.")
        return nome

    def clean_immagine_profilo(self):
        immagine_profilo = self.cleaned_data.get('immagine_profilo')
        if immagine_profilo:
            # verifica l'estensione del file
            file_name, file_extension = os.path.splitext(immagine_profilo.name)
            if file_extension.lower() not in ['.png', '.jpeg', '.jpg']:
                raise forms.ValidationError("L'estensione del file non è supportata. Utilizza file .png, .jpeg o .jpg.")
        return immagine_profilo