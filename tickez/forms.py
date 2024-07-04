from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from users.models import Utente

class CustomerCreationForm(UserCreationForm):
    nome = forms.CharField(max_length=100, required=True)
    cognome = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=254, required=True)
    data_nascita = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    sesso = forms.ChoiceField(choices=Utente.GENDER_CHOICES, required=False)
    stato = forms.CharField(max_length=100, required=True)
    indirizzo = forms.CharField(max_length=50, required=False)
    telefono = forms.CharField(max_length=20, required=False)
    carta_credito = forms.CharField(max_length=16, required=False)
    cvv = forms.CharField(max_length=3, required=False)
    scadenza_carta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = User
        # username, password1 e password2 possono essere inclusi anche tramite 'fields = UserCreationForm.Meta.fields + (...)'
        fields = (
            'nome', 'cognome', 'username', 'email', 'password1', 'password2', 
            'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono', 'carta_credito', 'cvv', 'scadenza_carta'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            utente = Utente(
                user=user,
                nome=self.cleaned_data['nome'],
                cognome=self.cleaned_data['cognome'],
                email=self.cleaned_data['email'],
                data_nascita=self.cleaned_data['data_nascita'],
                sesso=self.cleaned_data['sesso'],
                stato=self.cleaned_data['stato'],
                indirizzo=self.cleaned_data['indirizzo'],
                telefono=self.cleaned_data['telefono'],
                carta_credito=self.cleaned_data['carta_credito'],
                cvv=self.cleaned_data['cvv'],
                scadenza_carta=self.cleaned_data['scadenza_carta']
            )
            utente.save()
        return user