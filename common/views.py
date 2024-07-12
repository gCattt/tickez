from typing import Any
from django.shortcuts import render

from django.views.generic import ListView, DetailView

from common.models import Luogo
from products.models import Evento
from users.models import Organizzatore

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def common(request):
    return render(request, template_name="common/base_common.html")

class VenuesListView(ListView):
    model = Luogo
    template_name = 'common/venues.html' 
    paginate_by = 3

    def get_queryset(self):
        venue_list = super().get_queryset()
        
        return venue_list.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class VenueDetailView(DetailView):
    model = Luogo
    template_name = "common/venue_details.html"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.get_object().nome

        events = self.get_object().eventi_programmati.all()
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

    total_events = events.count()
    total_artists = artists.count()
    total_venues = venues.count()
    
    # paginazione dei risultati
    events_paginator = Paginator(events.order_by('data_ora'), 5)
    artists_paginator = Paginator(artists.order_by('nome'), 10)
    venues_paginator = Paginator(venues.order_by('nome'), 10)

    page_events = request.GET.get('page_events')
    page_artists = request.GET.get('page_artists')
    page_venues = request.GET.get('page_venues')

    try:
        events = events_paginator.page(page_events)
    except PageNotAnInteger:
        events = events_paginator.page(1)
    except EmptyPage:
        events = events_paginator.page(events_paginator.num_pages)

    try:
        artists = artists_paginator.page(page_artists)
    except PageNotAnInteger:
        artists = artists_paginator.page(1)
    except EmptyPage:
        artists = artists_paginator.page(artists_paginator.num_pages)

    try:
        venues = venues_paginator.page(page_venues)
    except PageNotAnInteger:
        venues = venues_paginator.page(1)
    except EmptyPage:
        venues = venues_paginator.page(venues_paginator.num_pages)

    return render(request, 'common/search_results.html', {
        'events': events, 
        'venues': venues, 
        'artists': artists, 
        'keywords': keywords,
        'total_events': total_events,
        'total_artists': total_artists,
        'total_venues': total_venues,
    })