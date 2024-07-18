from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse_lazy

from django.contrib import messages
from urllib.parse import urlparse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from braces.views import SuperuserRequiredMixin

from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django.contrib.auth.models import User
from users.models import Organizzatore
from common.models import Luogo
from products.models import Evento

from django.core.paginator import Paginator

from .forms import *


def users(request):
    return render(request, '404.html', status=404)


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"]
        # verifica se l'utente esiste nel sistema e se le credenziali fornite sono corrette
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                # verifica che il next_url sia un URL sicuro (relativo)
                parsed_next_url = urlparse(next_url)
                if parsed_next_url.path.startswith('/'):
                    return redirect(next_url)
            messages.success(request, 'Accesso effettuato con successo. Bentornato su Tickez!')
            return redirect('homepage')
        else:
            messages.error(request, ("Si è verificato un errore. Riprova"))
            return redirect('users:login')
    else:
        return render(request, 'users/registration/login.html', {})
    

class CustomerCreateView(CreateView):
    form_class = CustomerCreationForm
    template_name = "users/registration/user_create.html"
    success_url = reverse_lazy("homepage")

    # aggiunge logica eseguita prima di ogni richiesta
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "Effettua il logout per poter registrare un nuovo profilo.")
            return redirect("homepage")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Registrazione avvenuta con successo. Benvenuto su Tickez!")
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Utente'
        return context
    
    
class OrganizerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "is_staff" # solo l'admin (is_staff di default) può registrare gli organizzatori
    form_class = OrganizerCreationForm
    template_name = "users/registration/user_create.html"
    success_url = reverse_lazy("homepage")

    def form_valid(self, form):
        user = form.save()
        login(self.request, self.request.user)
        messages.success(self.request, "Account Organizzatore creato con successo!")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Organizzatore'
        return context
    

def is_customer(user):
    return user.groups.filter(name="Clienti").exists()

@user_passes_test(is_customer)
def toggle_follow(request, entity_type, entity_pk):
    # mappa il tipo di entità al modello corrispondente
    entity_model = {
        'evento': Evento,
        'organizzatore': Organizzatore,
        'luogo': Luogo,
    }
    try:
        entity = get_object_or_404(entity_model[entity_type], pk=entity_pk)

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
    except KeyError:
        return render(request, '404.html', status=404)
    except Http404:
        return render(request, '404.html', status=404)


class AdminProfileView(SuperuserRequiredMixin, DetailView):
    model = User
    template_name = 'users/admin_profile.html'
    success_url = reverse_lazy('users:admin-profile')

    def get_object(self, queryset=None):
        return self.request.user
    

class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    orders_per_page = 5 # ordini
    events_per_page = 4 # eventi
    starred_per_page = 8 # artisti e luoghi

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return render(request, '404.html', status=404)

    def get_object(self, queryset=None):
        if hasattr(self.request.user, 'organizzatore'):
            return get_object_or_404(Organizzatore, user=self.request.user)
        else:
            return get_object_or_404(Utente, user=self.request.user)

    def get_form_class(self):
        if hasattr(self.request.user, 'organizzatore'):
            return OrganizzatoreEditCrispyForm
        else:
            return CustomerEditCrispyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_owner = self.get_object()

        context['is_organizer'] = hasattr(self.request.user, 'organizzatore')
        context['user'] = self.request.user
        context['immagine_profilo'] = profile_owner.immagine_profilo_url

        orders_paginator = Paginator(profile_owner.ordini.order_by('-data_ora'), self.orders_per_page)
        context['orders'] = orders_paginator.get_page(self.request.GET.get('page_orders'))

        if hasattr(self.request.user, 'organizzatore'):
            events_paginator = Paginator(profile_owner.eventi_organizzati.order_by('data_ora'), self.starred_per_page)
            context['events'] = events_paginator.get_page(self.request.GET.get('page_events'))
        else:
            starred_events_paginator = Paginator(profile_owner.eventi_preferiti.order_by('data_ora'), self.events_per_page)
            context['starred_events'] = starred_events_paginator.get_page(self.request.GET.get('page_starred_events'))

            starred_artists_paginator = Paginator(profile_owner.organizzatori_preferiti.order_by('nome'), self.starred_per_page)
            context['starred_artists'] = starred_artists_paginator.get_page(self.request.GET.get('page_starred_artists'))

            starred_locations_paginator = Paginator(profile_owner.luoghi_preferiti.order_by('nome'), self.starred_per_page)
            context['starred_locations'] = starred_locations_paginator.get_page(self.request.GET.get('page_starred_locations'))
       
        return context
    

class ArtistsListView(ListView):
    model = Organizzatore
    template_name = 'users/artists.html' 
    paginate_by = 8

    def get_queryset(self):
        artist_list = super().get_queryset()
        
        return artist_list.order_by('nome')
    

class ArtistDetailView(DetailView):
    model = Organizzatore
    template_name = "users/artist_details.html"
    paginate_by = 4

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return render(request, '404.html', status=404)

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        pk = self.kwargs.get('pk')
        return get_object_or_404(Organizzatore, slug=slug, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.object.nome

        events = self.object.eventi_organizzati.order_by('data_ora')
        paginator = Paginator(events, self.paginate_by)
        events = paginator.get_page(self.request.GET.get('page'))
        
        context['planned_events'] = events

        return context