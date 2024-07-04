from django import forms
from django.contrib.auth.models import Group
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
        model = Utente
        # username, password1 e password2 possono essere inclusi anche tramite 'fields = UserCreationForm.Meta.fields + (...)'
        fields = (
            'nome', 'cognome', 'username', 'email', 'password1', 'password2', 
            'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono', 'carta_credito', 'cvv', 'scadenza_carta'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nome = self.cleaned_data['nome']
        user.cognome = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        user.data_nascita = self.cleaned_data['data_nascita']
        user.sesso = self.cleaned_data['sesso']
        user.stato = self.cleaned_data['stato']
        user.indirizzo = self.cleaned_data['indirizzo']
        user.telefono = self.cleaned_data['telefono']
        user.carta_credito = self.cleaned_data['carta_credito']
        user.cvv = self.cleaned_data['cvv']
        user.scadenza_carta = self.cleaned_data['scadenza_carta']
        if commit:
            user.save()
            #group = Group.objects.get(name="Clienti")
            #user.groups.add(group)
        return user