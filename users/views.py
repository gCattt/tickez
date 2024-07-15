from django.shortcuts import render
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, DetailView, UpdateView

from django.contrib.auth.models import User
from users.models import Organizzatore

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import *


def users(request):
    return render(request, template_name="users/base_users.html")


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

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    

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