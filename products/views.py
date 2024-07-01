from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from products.models import Evento, Biglietto

from django.views.generic import ListView, DetailView, UpdateView, DeleteView

from .forms import *

from datetime import datetime, timedelta

def products(request):
    #return HttpResponse("products test view.")
    return render(request, template_name="products/base_products.html")


class EventsListView(ListView):
    model = Evento
    template_name = 'products/events.html' 
    paginate_by = 3

    def get_queryset(self):
        event_list = super().get_queryset()

        order_by = self.request.GET.get('sort', 'data_ora')

        city = self.request.GET.get('city', '')

        category = self.request.GET.get('category', '')

        from_date = self.request.GET.get('from_date', '')
        until_date = self.request.GET.get('until_date', '')

        event_list = ( self.order_style(event_list, order_by) &
                       self.filter_by_city(event_list, city) &
                       self.filter_by_category(event_list, category) &
                       self.filter_by_date(event_list, from_date, until_date)
        )
        return event_list
    
    def order_style(self, queryset, order_by):
        if order_by == 'nome':
            return queryset.order_by('nome')
        else:
            return queryset.order_by('data_ora')

    def filter_by_city(self, queryset, city):
        if city:
            return queryset.filter(luogo__citta__icontains=city)
        return queryset

    def filter_by_category(self, queryset, category):
        if category:
            return queryset.filter(categoria=category)
        return queryset
    
    def filter_by_date(self, queryset, from_date, until_date):
        if from_date:
            queryset = queryset.filter(data_ora__gte=datetime.strptime(from_date, '%d/%m/%Y'))
        if until_date:
            queryset = queryset.filter(data_ora__lte=datetime.strptime(until_date, '%d/%m/%Y'))
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['current_sort'] = self.request.GET.get('sort', 'data_ora')
        context['current_city'] = self.request.GET.get('city', '')
        context['current_category'] = self.request.GET.get('category', '')

        context['cities'] = sorted(Evento.objects.values_list('luogo__citta', flat=True).distinct())
        context['categories'] = sorted(Evento.objects.values_list('categoria', flat=True).distinct())
        
        context['current_from'] = self.request.GET.get('from_date', '')
        context['current_until'] = self.request.GET.get('until_date', '')

        return context
    
class EventDetailView(DetailView):
    model = Evento
    template_name = "products/event_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = str(self.get_object().organizzatore) + ' - ' + self.get_object().nome
        context['tickets'] = self.get_object().biglietti_disponibili.all()
        context['range_dropdown'] = range(0, 6)
        context['name_change'] = self.get_object().data_ora - timedelta(days=15)

        return context
    

def create_event(request):
    entity = 'Evento'
    if request.method == 'POST':
        form = EventCrispyForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            # event.organizzatore = <utente_attuale> --> poi rimuovi organizzatore dal form
            event.save()

            return redirect(event.get_absolute_url())
    else:
        form = EventCrispyForm()
    
    return render(request, 'products/create_entity.html', {'form': form, 'entity': entity})

def create_ticket(request, event_slug, event_pk):
    entity = 'Biglietto'
    event = get_object_or_404(Evento, slug=event_slug, pk=event_pk)

    if request.method == 'POST':
        form = TicketCrispyForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.evento = event
            ticket.organizzatore = event.organizzatore
            ticket.save()
            return redirect(ticket.get_absolute_url())
    else:
        form = TicketCrispyForm()

    return render(request, 'products/create_entity.html', {'form': form, 'entity': entity, 'event': event})


class UpdateEventView(UpdateView):
    model = Evento
    form_class = EventCrispyForm
    template_name = "products/update_entity.html"
    
    def get_success_url(self):
        return self.get_object().get_absolute_url()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = 'Salva Modifiche'
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Evento'+self.nome
        return context
    
class UpdateTicketView(UpdateView):
    model = Biglietto
    form_class = TicketCrispyForm
    template_name = "products/update_entity.html"
    slug_field = 'slug'

    def get_object(self, queryset=None):
        self.event = get_object_or_404(Evento, slug=self.kwargs.get('event_slug'), pk=self.kwargs.get('event_pk'))

        queryset = self.event.biglietti_disponibili.all()
        ticket = get_object_or_404(queryset, slug=self.kwargs.get('ticket_slug'), pk=self.kwargs.get('ticket_pk'))

        return ticket

    def get_success_url(self):
        return self.event.get_absolute_url()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = 'Salva Modifiche'
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Biglietto'
        return context
    

class DeleteEventView(DeleteView):
    model = Evento
    template_name = "products/delete_entity.html"
    success_url = reverse_lazy('products:events')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Evento'
        context['name'] = self.object.nome
        return context

class DeleteTicketView(DeleteView):
    model = Biglietto
    template_name = "products/delete_entity.html"

    def get_object(self, queryset=None):
        self.event = get_object_or_404(Evento, slug=self.kwargs.get('event_slug'), pk=self.kwargs.get('event_pk'))

        queryset = self.event.biglietti_disponibili.all()
        ticket = get_object_or_404(queryset, slug=self.kwargs.get('ticket_slug'), pk=self.kwargs.get('ticket_pk'))

        return ticket

    # get_success_url permette di determinare l'URL di reindirizzamento in modo dinamico, basandosi sull'oggetto manipolato (a differenza di reverse_lazy)
    def get_success_url(self):
        return self.event.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Biglietto'
        context['name'] = self.object.tipologia+' ('+self.object.evento.nome+')'
        return context