from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import CreateView

from django.contrib import messages

from products.models import Evento

from .forms import *

def home_page(request):
    home_page_events = Evento.objects.order_by('data_ora')[:5]

    templ = "common/home_page.html"
    ctx = {"object_list": home_page_events}

    return render(request, template_name=templ, context=ctx)


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # verificare se l'utente esiste nel sistema e se le credenziali fornite sono corrette
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, ("Si è verificato un errore. Riprova"))
            return redirect('login')
            
    else:
        return render(request, 'registration/login.html', {})
    
class UserCreateView(CreateView):
    form_class = CustomerCreationForm
    template_name = "registration/user_create.html"
    success_url = reverse_lazy("homepage")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Account creato con successo!")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Si è verificato un errore. Per favore, correggi i campi evidenziati.")
        # renderizzare il template con il contesto aggiornato (messaggi di errore e campi errati ripuliti)
        return self.render_to_response(self.get_context_data(form=form)) 