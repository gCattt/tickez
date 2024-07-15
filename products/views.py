from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
#from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from products.models import Evento, Biglietto
from users.models import Organizzatore
from common.models import Notifica
from orders.models import BigliettoAcquistato

from django.db.models import Count, Sum
from django.db.models.functions import TruncDay

from django.views.generic import ListView, DetailView, UpdateView, DeleteView

from .forms import *

from products.filters import EventoFilter

from datetime import datetime, timedelta
from django.utils import timezone


def products(request):
    return render(request, template_name="products/base_products.html")

class EventsListView(ListView):
    model = Evento
    template_name = 'products/events.html' 
    paginate_by = 1

    def get_queryset(self):
        queryset = super().get_queryset().order_by('data_ora')
        self.evento_filter = EventoFilter(self.request.GET, queryset=queryset)
        return self.evento_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.evento_filter
        return context
    
class EventDetailView(DetailView):
    model = Evento
    template_name = "products/event_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        evento = self.get_object()

        evento.visualizzazioni += 1
        evento.save()

        if self.request.user.is_authenticated:
            try:
                utente = self.request.user.utente
                evento = self.get_object()
                notification = Notifica.objects.filter(evento=evento, organizzatore__in=utente.organizzatori_preferiti.all()).first()
                if notification and not notification.letta:
                    notification.letta = True
                    notification.save()
            except:
                utente = None

        context['title'] = str(self.get_object().organizzatore) + ' - ' + self.get_object().nome
        context['tickets'] = self.get_object().biglietti_disponibili.all()
        context['range_dropdown'] = range(0, 6)
        context['name_change'] = self.get_object().data_ora - timedelta(days=15)

        return context
    
# funzione di test per gestire l'autenticazione di admin ed organizzatori
def is_allowed(user):
    return user.is_superuser or user.groups.filter(name="Organizzatori").exists()

# mixin personalizzato per gestire l'autenticazione di admin ed organizzatori
class OrganizerOrSuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        obj = self.get_object()
        return user.is_superuser or (user.groups.filter(name="Organizzatori").exists() and obj.organizzatore.user == user)
    
    login_url = reverse_lazy('login')

    # se l'utente è autenticato ma non ha i permessi, solleva PermissionDenied
    def handle_no_permission(self):
        # in caso di tentato accesso ad una view protetta, senza i permessi adatti, reindirizza al login
        return redirect(f'{self.login_url}?auth=notok&next={self.request.path}')
    
def notify(event):
    organizzatore = event.organizzatore
    notification_text = f"Nuovo evento di {organizzatore.nome}: {event.nome} | Scopri i dettagli e Acquista!"

    Notifica.objects.create(
        testo=notification_text,
        data_ora=timezone.now(),
        organizzatore=organizzatore,
        luogo=event.luogo,
        evento=event
    )
    
@user_passes_test(is_allowed)
def create_event(request):
    entity = 'Evento'
    if request.method == 'POST':
        if request.user.is_superuser:
            form = AdminEventCrispyForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save()

                notify(event)

                return redirect(event.get_absolute_url())
        else:
            form = EventCrispyForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                organizzatore = Organizzatore.objects.get(user=request.user) # istanza di Organizzatore associata a User
                event.organizzatore = organizzatore
                event.save()

                notify(event)

                return redirect(event.get_absolute_url())
    else:
        if request.user.is_superuser:
            form = AdminEventCrispyForm()
        else:
            form = EventCrispyForm()
    
    return render(request, 'products/create_entity.html', {'form': form, 'entity': entity})

@user_passes_test(is_allowed)
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

class UpdateEventView(OrganizerOrSuperuserRequiredMixin, UpdateView):
    model = Evento
    template_name = "products/update_entity.html"

    # sovrascrive get_form_class per determinare il form da utilizzare sulla base di self.request.user
    def get_form_class(self):
        if self.request.user.is_superuser:
            return AdminEventCrispyForm
        return EventCrispyForm
    
    def get_success_url(self):
        return self.get_object().get_absolute_url()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = 'Salva Modifiche'
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Evento'
        context['name'] = self.object.nome
        return context
    
class UpdateTicketView(OrganizerOrSuperuserRequiredMixin, UpdateView):
    model = Biglietto
    form_class = TicketCrispyForm
    template_name = "products/update_entity.html"
    slug_field = 'slug'

    def get_object(self, queryset=None):
        self.event = get_object_or_404(Evento, slug=self.kwargs.get('event_slug'), pk=self.kwargs.get('event_pk'))

        queryset = self.event.biglietti_disponibili.filter(slug=self.kwargs.get('ticket_slug'))
        ticket = get_object_or_404(queryset, pk=self.kwargs.get('ticket_pk'))

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
        context['name'] = self.object.tipologia
        return context
    
class DeleteEventView(OrganizerOrSuperuserRequiredMixin, DeleteView):
    model = Evento
    template_name = "products/delete_entity.html"
    success_url = reverse_lazy('products:events')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Evento'
        context['name'] = self.object.nome
        return context

class DeleteTicketView(OrganizerOrSuperuserRequiredMixin, DeleteView):
    model = Biglietto
    template_name = "products/delete_entity.html"

    def get_object(self, queryset=None):
        self.event = get_object_or_404(Evento, slug=self.kwargs.get('event_slug'), pk=self.kwargs.get('event_pk'))

        queryset = self.event.biglietti_disponibili.filter(slug=self.kwargs.get('ticket_slug'))
        ticket = get_object_or_404(queryset, pk=self.kwargs.get('ticket_pk'))

        return ticket

    # get_success_url permette di determinare l'URL di reindirizzamento in modo dinamico, basandosi sull'oggetto manipolato (a differenza di reverse_lazy)
    def get_success_url(self):
        return self.event.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Biglietto'
        context['name'] = self.object.tipologia+' ('+self.object.evento.nome+')'
        return context
    
@user_passes_test(is_allowed)
def event_statistics(request, slug, pk):
    evento = Evento.objects.get(id=pk)

    visualizzazioni_evento = evento.visualizzazioni
    biglietti_venduti = BigliettoAcquistato.objects.filter(biglietto__evento=evento).count()
    revenue_totale = BigliettoAcquistato.objects.filter(biglietto__evento=evento).aggregate(Sum('biglietto__prezzo'))['biglietto__prezzo__sum'] or 0
    
    # calcolo delle fasce di età dei partecipanti
    current_year = datetime.now().year
    fasce_eta = {
        '0_18': BigliettoAcquistato.objects.filter(
            biglietto__evento=evento,
            ordine__utente__data_nascita__year__gte=current_year - 18
        ).values('nome_acquirente', 'cognome_acquirente').distinct().count(),

        '19_35': BigliettoAcquistato.objects.filter(
            biglietto__evento=evento,
            ordine__utente__data_nascita__year__range=[current_year - 35, current_year - 19]
        ).values('nome_acquirente', 'cognome_acquirente').distinct().count(),

        '36_50': BigliettoAcquistato.objects.filter(
            biglietto__evento=evento,
            ordine__utente__data_nascita__year__range=[current_year - 50, current_year - 36]
        ).values('nome_acquirente', 'cognome_acquirente').distinct().count(),

        '50_plus': BigliettoAcquistato.objects.filter(
            biglietto__evento=evento,
            ordine__utente__data_nascita__year__lt=current_year - 50
        ).values('nome_acquirente', 'cognome_acquirente').distinct().count(),
    }
    
    # nazionalità dei partecipanti (esempio con 5 nazionalità più comuni)
    nazionalita_partecipanti = (
    BigliettoAcquistato.objects
        .filter(biglietto__evento=evento)
        .values('ordine__utente__stato', 'nome_acquirente', 'cognome_acquirente')
        .distinct()
        .annotate(count=Count('ordine__utente__stato'))
        .order_by('-count')[:5]
    )

    # sesso dei partecipanti
    sesso_partecipanti = (
        BigliettoAcquistato.objects
        .filter(biglietto__evento=evento)
        .values('ordine__utente__sesso', 'nome_acquirente', 'cognome_acquirente')
        .distinct()
        .annotate(count=Count('ordine__utente__sesso'))
    )

    # biglietti venduti per ogni tipologia
    biglietti_acquistati = BigliettoAcquistato.objects.filter(biglietto__evento=evento)
    
    vendite_per_tipologia = {}
    for biglietto_acquistato in biglietti_acquistati:
        tipologia = biglietto_acquistato.biglietto.tipologia
        if tipologia not in vendite_per_tipologia:
            vendite_per_tipologia[tipologia] = 0
        vendite_per_tipologia[tipologia] += 1

    # vendite giornaliere
    vendite_per_giorno = (
        BigliettoAcquistato.objects.filter(biglietto__evento=evento)
        .annotate(giorno=TruncDay('data_acquisto'))
        .values('giorno')
        .annotate(count=Count('id'))
        .order_by('giorno')
    )
    # dati fittizi per il test
    test_data = [
        {'giorno': timezone.datetime(2024, 7, 1, 0, 0), 'count': 10},
        {'giorno': timezone.datetime(2024, 7, 8, 0, 0), 'count': 15},
        {'giorno': timezone.datetime(2024, 8, 22, 0, 0), 'count': 25},
        {'giorno': timezone.datetime(2024, 9, 25, 0, 0), 'count': 5},
    ]
    vendite_per_giorno = list(vendite_per_giorno) + test_data

    context = {
        'evento': evento,
        'visualizzazioni_evento': visualizzazioni_evento,
        'biglietti_venduti': biglietti_venduti,
        'revenue_totale': revenue_totale,
        'fasce_eta': fasce_eta,
        'nazionalita_partecipanti': nazionalita_partecipanti,
        'sesso_partecipanti': sesso_partecipanti,
        'vendite_per_tipologia': vendite_per_tipologia,
        'vendite_per_giorno': vendite_per_giorno,
    }

    return render(request, 'products/event_statistics.html', context)