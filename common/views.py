from typing import Any
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from common.models import Luogo


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