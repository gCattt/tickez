from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.contrib import messages
from urllib.parse import urlparse, parse_qs

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import CreateView

from products.models import Evento
from users.models import Organizzatore
from common.models import Luogo

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
            next_url = request.GET.get('next')
            if next_url:
                # verifica che il next_url sia un URL sicuro (relativo)
                parsed_next_url = urlparse(next_url)
                if parsed_next_url.path.startswith('/'):
                    return redirect(next_url)
            return redirect('homepage')
        else:
            messages.error(request, ("Si è verificato un errore. Riprova"))
            return redirect('login')
    else:
        return render(request, 'registration/login.html', {})
    

class CustomerCreateView(CreateView):
    form_class = CustomerCreationForm
    template_name = "registration/user_create.html"
    success_url = reverse_lazy("homepage")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Account creato con successo!")
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Utente'
        return context
    
class OrganizerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "is_staff" # solo l'admin (is_staff di default) può registrare gli organizzatori
    form_class = OrganizerCreationForm
    template_name = "registration/user_create.html"
    success_url = reverse_lazy("homepage")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Account Organizzatore creato con successo!")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Organizzatore'
        return context
    

@login_required
def toggle_follow(request, entity_type, entity_pk):
    # mappa il tipo di entità al modello corrispondente
    entity_model = {
        'evento': Evento,
        'organizzatore': Organizzatore,
        'luogo': Luogo,
    }

    entity = get_object_or_404(entity_model[entity_type], id=entity_pk)

    if request.method == "POST":
        if request.POST.get('action') == 'follow':
            if request.user.utente not in entity.followers.all():
                entity.followers.add(request.user.utente)
                return redirect(entity.get_absolute_url())
        elif request.POST.get('action') == 'unfollow':
            if request.user.utente in entity.followers.all():
                entity.followers.remove(request.user.utente)
                return redirect(entity.get_absolute_url())
            
    return redirect(entity.get_absolute_url())