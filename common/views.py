from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from django.views.generic import ListView, DetailView

from common.models import Luogo
from products.models import Evento
from users.models import Organizzatore

from django.core.paginator import Paginator

from products.filters import EventoFilter


def common(request):
    return render(request, '404.html', status=404)

# elenco luoghi, in ordine alfabetico
class VenuesListView(ListView):
    model = Luogo
    template_name = 'common/venues.html' 
    paginate_by = 8

    def get_queryset(self):
        venue_list = super().get_queryset()
        
        return venue_list.order_by('nome')
    
# dettagli luogo
class VenueDetailView(DetailView):
    model = Luogo
    template_name = "common/venue_details.html"
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
        return get_object_or_404(Luogo, slug=slug, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.get_object().nome

        events = self.get_object().eventi_programmati.order_by('data_ora')
        paginator = Paginator(events, self.paginate_by)
        # con get_page django gestisce internamente le eccezioni e garantisce che venga sempre restituita una pagina valida.
        events = paginator.get_page(self.request.GET.get('page'))

        context['planned_events'] = events

        return context
    
# funzionalità di ricerca tramite 'keywords'
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

    # applicazione del form di filtraggio agli eventi
    evento_filter = EventoFilter(request.GET, queryset=events)
    events = evento_filter.qs

    total_events = events.count()
    total_artists = artists.count()
    total_venues = venues.count()
    
    # paginazione dei risultati
    events_paginator = Paginator(events, 5)
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