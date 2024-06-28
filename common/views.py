from typing import Any
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from common.models import Luogo
from products.models import Evento
from users.models import Organizzatore


def common(request):
    #return HttpResponse("common test view.")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.get_object().nome
        context['planned_events'] = self.get_object().eventi_programmati.all()

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
            venues = venues.filter(nome__icontains=term)
            artists = artists.filter(nome__icontains=term)

    return render(request, 'common/search_results.html', {
        'events': events.order_by('data_ora'), 
        'venues': venues.order_by('nome'), 
        'artists': artists.order_by('nome'), 
        'keywords': keywords})