from typing import Any
from django.shortcuts import render

from django.views.generic import ListView, DetailView

from common.models import Luogo
from products.models import Evento
from users.models import Organizzatore

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from products.filters import EventoFilter


def common(request):
    return render(request, template_name="common/base_common.html")

class VenuesListView(ListView):
    model = Luogo
    template_name = 'common/venues.html' 
    paginate_by = 8

    def get_queryset(self):
        venue_list = super().get_queryset()
        
        return venue_list.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class VenueDetailView(DetailView):
    model = Luogo
    template_name = "common/venue_details.html"
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.get_object().nome

        events = self.get_object().eventi_programmati.order_by('data_ora')
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
    
def search_results(request):
    events = Evento.objects.all()
    venues = Luogo.objects.all()
    artists = Organizzatore.objects.all()
    keywords = request.GET.get('keywords', '').strip()
    
    if keywords:
        search_terms = keywords.split()

        for term in search_terms:
            events = events.filter(nome__icontains=term)
            artists = artists.filter(nome__icontains=term)
            venues = venues.filter(nome__icontains=term)

    evento_filter = EventoFilter(request.GET, queryset=events)
    events = evento_filter.qs

    total_events = events.count()
    total_artists = artists.count()
    total_venues = venues.count()
    
    # paginazione dei risultati
    events_paginator = Paginator(events.order_by('data_ora'), 5)
    artists_paginator = Paginator(artists.order_by('nome'), 8)
    venues_paginator = Paginator(venues.order_by('nome'), 8)

    # con get_page django gestisce internamente le eccezioni e garantisce che venga sempre restituita una pagina valida.
    events = events_paginator.get_page(request.GET.get('page_events'))
    artists = artists_paginator.get_page(request.GET.get('page_artists'))
    venues = venues_paginator.get_page(request.GET.get('page_venues'))

    return render(request, 'common/search_results.html', {
        'events': events, 
        'venues': venues, 
        'artists': artists, 
        'keywords': keywords,
        'total_events': total_events,
        'total_artists': total_artists,
        'total_venues': total_venues,
        'filter': evento_filter,
    })