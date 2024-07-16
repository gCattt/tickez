from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.contrib import messages
from urllib.parse import urlparse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django.contrib.auth.models import User
from users.models import Organizzatore
from common.models import Luogo
from products.models import Evento

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import *


def users(request):
    return render(request, template_name="users/base_users.html")


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
        messages.success(self.request, "Account creato con successo!")
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


class AdminProfileView(LoginRequiredMixin, DetailView):
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

    def get_object(self, queryset=None):
        if hasattr(self.request.user, 'organizzatore'):
            return self.request.user.organizzatore
        else:
            return self.request.user.utente

    def get_form_class(self):
        if hasattr(self.request.user, 'organizzatore'):
            return OrganizzatoreEditCrispyForm
        else:
            return CustomerEditCrispyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'organizzatore'):
            organizzatore = self.get_object()
            context['is_organizer'] = True
            context['user'] = self.request.user
            context['immagine_profilo'] = organizzatore.immagine_profilo_url

            orders_paginator = Paginator(organizzatore.ordini.order_by('-data_ora'), self.orders_per_page)
            context['orders'] = orders_paginator.get_page(self.request.GET.get('page_orders'))

            events_paginator = Paginator(organizzatore.eventi_organizzati.order_by('data_ora'), self.starred_per_page)
            context['events'] = events_paginator.get_page(self.request.GET.get('page_events'))
        else:
            utente = self.get_object()
            context['is_organizer'] = False
            context['user'] = self.request.user
            context['immagine_profilo'] = utente.immagine_profilo_url

            orders_paginator = Paginator(utente.ordini.order_by('-data_ora'), self.orders_per_page)
            context['orders'] = orders_paginator.get_page(self.request.GET.get('page_orders'))

            starred_events_paginator = Paginator(utente.eventi_preferiti.order_by('data_ora'), self.events_per_page)
            context['starred_events'] = starred_events_paginator.get_page(self.request.GET.get('page_starred_events'))

            starred_artists_paginator = Paginator(utente.organizzatori_preferiti.order_by('nome'), self.starred_per_page)
            context['starred_artists'] = starred_artists_paginator.get_page(self.request.GET.get('page_starred_artists'))

            starred_locations_paginator = Paginator(utente.luoghi_preferiti.order_by('nome'), self.starred_per_page)
            context['starred_locations'] = starred_locations_paginator.get_page(self.request.GET.get('page_starred_locations'))
       
        return context
    

class ArtistsListView(ListView):
    model = Organizzatore
    template_name = 'users/artists.html' 
    paginate_by = 8

    def get_queryset(self):
        artist_list = super().get_queryset()
        
        return artist_list.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class ArtistDetailView(DetailView):
    model = Organizzatore
    template_name = "users/artist_details.html"
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.get_object().nome

        events = self.get_object().eventi_organizzati.order_by('data_ora')
        paginator = Paginator(events, self.paginate_by)

        page = self.request.GET.get('page')
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            # se la pagina non è un numero intero, mostra la prima pagina
            events = paginator.page(1)
        except EmptyPage:
            # se la pagina è vuota, mostra l'ultima pagina disponibile
            events = paginator.page(paginator.num_pages)
        
        context['planned_events'] = events

        return context