from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse_lazy

from django.contrib import messages

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

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

from django.conf import settings


def products(request):
    return render(request, '404.html', status=404)

class EventsListView(ListView):
    model = Evento
    template_name = 'products/events.html' 
    paginate_by = 5

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

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect('404')

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        pk = self.kwargs.get('pk')
        return get_object_or_404(Evento, slug=slug, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evento = self.object

        evento.visualizzazioni += 1
        evento.save()

        if self.request.user.is_authenticated:
            try:
                utente = self.request.user.utente
                notification = Notifica.objects.filter(evento=evento, organizzatore__in=utente.organizzatori_preferiti.all()).first()
                if notification and not notification.letta:
                    notification.letta = True
                    notification.save()
            except:
                utente = None

        context['title'] = f"{evento.organizzatore} - {evento.nome}"
        context['tickets'] = evento.biglietti_disponibili.all()
        context['range_dropdown'] = range(0, 6)
        context['name_change'] = evento.data_ora - timedelta(days=15)

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

    # se l'utente è autenticato ma non ha i permessi, solleva PermissionDenied
    def handle_no_permission(self):
        # in caso di tentato accesso ad una view protetta, senza i permessi adatti, reindirizza al login
        return redirect(f'{settings.LOGIN_URL}&next={self.request.path}')
    
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
    form_class = AdminEventCrispyForm if request.user.is_superuser else EventCrispyForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            if request.user.is_superuser:
                event.save()
                messages.success(request, f'Evento "{event.nome}" creato con successo!')
            else:
                try:
                    organizzatore = get_object_or_404(Organizzatore, user=request.user)
                    event.organizzatore = organizzatore
                    event.save()
                    messages.success(request, f'Evento "{event.nome}" creato con successo!')
                except Http404:
                    return redirect('404')
            
            notify(event)
            return redirect(event.get_absolute_url())
        else:
            messages.error(request, 'Si è verificato un errore durante la creazione dell\'evento. Riprova.')
    else:
        form = form_class()
    
    return render(request, 'products/create_entity.html', {'form': form, 'entity': entity})


@user_passes_test(is_allowed)
def create_ticket(request, event_slug, event_pk):
    entity = 'Biglietto'
    try:
        event = get_object_or_404(Evento, slug=event_slug, pk=event_pk)
    except Http404:
        return redirect('404')

    if request.method == 'POST':
        form = TicketCrispyForm(request.POST, evento=event)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.evento = event
            ticket.organizzatore = event.organizzatore
            ticket.save()
            messages.success(request, f'Biglietto "{ticket.tipologia}" creato con successo!')
            return redirect(ticket.get_absolute_url())
        else:
            messages.error(request, 'Si è verificato un errore durante la creazione del biglietto. Riprova.')
    else:
        form = TicketCrispyForm()

    return render(request, 'products/create_entity.html', {'form': form, 'entity': entity, 'event': event})


class UpdateEventView(OrganizerOrSuperuserRequiredMixin, UpdateView):
    model = Evento
    template_name = "products/update_entity.html"

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect('404')

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        pk = self.kwargs.get('pk')
        return get_object_or_404(Evento, slug=slug, pk=pk)

    # sovrascrive get_form_class per determinare il form da utilizzare sulla base di self.request.user
    def get_form_class(self):
        return AdminEventCrispyForm if self.request.user.is_superuser else EventCrispyForm
    
    # il metodo form_valid è già implementato per gestire il salvataggio dell'istanza del modello
    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = 'Salva Modifiche'
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Evento'
        context['name'] = self.object.nome
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Modifiche salvate con successo!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Si è verificato un errore durante il salvataggio delle modifiche.')
        return super().form_invalid(form)
    

class UpdateTicketView(OrganizerOrSuperuserRequiredMixin, UpdateView):
    model = Biglietto
    form_class = TicketCrispyForm
    template_name = "products/update_entity.html"
    slug_field = 'slug'

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect('404')

    def get_object(self, queryset=None):
        self.event = get_object_or_404(Evento, slug=self.kwargs.get('event_slug'), pk=self.kwargs.get('event_pk'))
        queryset = self.event.biglietti_disponibili.filter(slug=self.kwargs.get('ticket_slug'))
        ticket = get_object_or_404(queryset, pk=self.kwargs.get('ticket_pk'))
        return ticket

    # il metodo form_valid è già implementato per gestire il salvataggio dell'istanza del modello
    def get_success_url(self):
        return self.event.get_absolute_url()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['evento'] = self.event
        kwargs['action'] = 'Salva Modifiche'
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Biglietto'
        context['name'] = self.object.tipologia
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Modifiche salvate con successo!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Si è verificato un errore durante il salvataggio delle modifiche.')
        return super().form_invalid(form)
    

class DeleteEventView(OrganizerOrSuperuserRequiredMixin, DeleteView):
    model = Evento
    template_name = "products/delete_entity.html"
    success_url = reverse_lazy('products:events')

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect('404')

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        pk = self.kwargs.get('pk')
        return get_object_or_404(Evento, slug=slug, pk=pk)
    
    def get_success_url(self):
        messages.success(self.request, f'Evento "{self.object.nome}" eliminato con successo!')
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Evento'
        context['name'] = self.object.nome
        return context


class DeleteTicketView(OrganizerOrSuperuserRequiredMixin, DeleteView):
    model = Biglietto
    template_name = "products/delete_entity.html"

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect('404')

    def get_object(self, queryset=None):
        self.event = get_object_or_404(Evento, slug=self.kwargs.get('event_slug'), pk=self.kwargs.get('event_pk'))
        queryset = self.event.biglietti_disponibili.filter(slug=self.kwargs.get('ticket_slug'))
        ticket = get_object_or_404(queryset, pk=self.kwargs.get('ticket_pk'))
        return ticket

    # get_success_url permette di determinare l'URL di reindirizzamento in modo dinamico, basandosi sull'oggetto manipolato (a differenza di reverse_lazy)
    def get_success_url(self):
        messages.success(self.request, f'Biglietto "{self.object.tipologia}" eliminato con successo.')
        return self.event.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Biglietto'
        context['name'] = f'{self.object.tipologia} ({self.object.evento.nome})'
        return context
    
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    

@user_passes_test(is_allowed)
def event_statistics(request, slug, pk):
    try:
        evento = get_object_or_404(Evento, slug=slug, pk=pk)

        visualizzazioni_evento = evento.visualizzazioni
        biglietti_venduti = BigliettoAcquistato.objects.filter(biglietto__evento=evento).count()
        revenue_totale = BigliettoAcquistato.objects.filter(biglietto__evento=evento).aggregate(Sum('biglietto__prezzo'))['biglietto__prezzo__sum'] or 0
        
        # calcolo delle fasce di età dei partecipanti
        current_year = datetime.now().year
        fasce_eta = {
            '0_18': BigliettoAcquistato.objects.filter(
                biglietto__evento=evento,
                data_nascita_acquirente__year__gte=current_year - 18
            ).values('nome_acquirente', 'cognome_acquirente', 'data_nascita_acquirente', 'sesso_acquirente').count(),

            '19_35': BigliettoAcquistato.objects.filter(
                biglietto__evento=evento,
                data_nascita_acquirente__year__range=[current_year - 35, current_year - 19]
            ).values('nome_acquirente', 'cognome_acquirente', 'data_nascita_acquirente', 'sesso_acquirente').count(),

            '36_50': BigliettoAcquistato.objects.filter(
                biglietto__evento=evento,
                data_nascita_acquirente__year__range=[current_year - 50, current_year - 36]
            ).values('nome_acquirente', 'cognome_acquirente', 'data_nascita_acquirente', 'sesso_acquirente').count(),

            '50_plus': BigliettoAcquistato.objects.filter(
                biglietto__evento=evento,
                data_nascita_acquirente__year__lt=current_year - 50
            ).values('nome_acquirente', 'cognome_acquirente', 'data_nascita_acquirente', 'sesso_acquirente').count(),
        }
        
        # nazionalità dei partecipanti (top 5)
        nazionalita_partecipanti = (
        BigliettoAcquistato.objects
            .filter(biglietto__evento=evento)
            .values('stato_acquirente')
            .annotate(count=Count('stato_acquirente'))
            .order_by('-count')[:5]
        )

        # sesso dei partecipanti
        sesso_partecipanti = (
            BigliettoAcquistato.objects
            .filter(biglietto__evento=evento)
            .values('sesso_acquirente')
            .annotate(count=Count('sesso_acquirente'))
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
    
    except Http404:
        return redirect('404')