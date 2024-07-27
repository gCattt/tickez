from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse_lazy

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from braces.views import GroupRequiredMixin

from .forms import CheckoutCrispyForm, BigliettoAcquistatoCrispyForm

from .models import Ordine, BigliettoAcquistato
from products.models import Biglietto
from users.models import Utente

from django.views.generic import UpdateView

from django.contrib import messages

from django.utils import timezone

from django.conf import settings


def orders(request):
    return render(request, '404.html', status=404)


# funzione di test per gestire l'autenticazione degli utenti
def is_customer(user):
    return user.groups.filter(name="Clienti").exists()

@user_passes_test(is_customer)
# raccolta dati per il riepilogo ordine
def checkout(request):
    if request.method == 'POST':
        selected_tickets = []
        total = 0
        flag_tickets = False  # verifica se sono stati selezionati dei biglietti

        # recupera id e quantità dei biglietti selezionati
        for key, value in request.POST.items():
            if key.startswith("quantita_") and int(value) > 0:
                ticket_id = key.split("_")[1]
                try:
                    biglietto = get_object_or_404(Biglietto, id=ticket_id)
                except Http404:
                    return render(request, '404.html', status=404)
                quantity = int(value)
                
                # verifica la quantità vendibile del biglietto considerato
                if quantity > biglietto.quantita_vendibile:
                    messages.error(request, f'La quantità richiesta per il biglietto "{biglietto.tipologia}" è maggiore della quantità attualmente disponibile ({biglietto.quantita_vendibile}).')
                    event_url = request.POST.get('evento_url')
                    return redirect(event_url)

                # se tutto va a buon fine aggiorna i biglietti selezionati ed il totale dell'ordine
                for _ in range(quantity):
                    selected_tickets.append(biglietto)
                    total += biglietto.prezzo
                flag_tickets = True

        if not flag_tickets:
            messages.error(request, 'Seleziona almeno un biglietto.')
            event_url = request.POST.get('evento_url')
            return redirect(event_url)

        # memorizza i biglietti selezionati nella sessione (gli id nello specifico, in quanto l'oggetto Biglietto non è serializzabile)
        request.session['selected_tickets'] = [t.id for t in selected_tickets]
        request.session['total'] = total
        
        form = CheckoutCrispyForm()
        return render(request, 'orders/checkout.html', {
            'selected_tickets': selected_tickets,
            'total': total,
            'form': form
        })

    return redirect('homepage')

@user_passes_test(is_customer)
# riepilogo ordine ed elaborazione pagamento
def process_payment(request):
    if request.method == 'POST':
        form = CheckoutCrispyForm(request.POST)
        if form.is_valid():
            # recupero dei dati della sessione
            selected_tickets = request.session.get('selected_tickets', [])
            total = request.session.get('total', 0)
            
            # ottieni l'istanza di Utente associata all'utente autenticato
            try:
                utente = get_object_or_404(Utente, user=request.user)
            except Http404:
                return render(request, '404.html', status=404)
            
            # ottieni l'organizzatore che ha creato i biglietti (basta il primo)
            try:
                biglietto = get_object_or_404(Biglietto, id=selected_tickets[0])
            except Http404:
                return render(request, '404.html', status=404)
            organizzatore = biglietto.organizzatore
            evento = biglietto.evento
            
            ordine = Ordine.objects.create(
                utente=utente,
                organizzatore=organizzatore,
                evento=evento,
                totale=total,
                data_ora=timezone.now()
            )
            
            # aggiorna la quantità dei biglietti e associa i biglietti acquistati all'ordine appena creato
            for ticket_id in selected_tickets:
                try:
                    biglietto = get_object_or_404(Biglietto, id=ticket_id)
                except Http404:
                    return render(request, '404.html', status=404)
                
                biglietto.quantita_vendibile -= 1
                biglietto.save()
            
                BigliettoAcquistato.objects.create(
                    biglietto=biglietto,
                    ordine=ordine,
                    nome_acquirente=utente.nome,
                    cognome_acquirente=utente.cognome,
                    data_nascita_acquirente=utente.data_nascita,
                    sesso_acquirente=utente.sesso,
                    stato_acquirente=utente.stato,
                    data_acquisto=timezone.now(),
                    prezzo_acquisto=biglietto.prezzo
                )
            
            messages.success(request, 'L\'ordine è stato effettuato con successo!')
            return redirect('homepage')
    else:
        form = CheckoutCrispyForm()

    # se il form non è valido, o non è un metodo POST, renderizza la pagina con il form e gli errori
    return render(request, 'orders/checkout.html', {'form': form})


# funzionalità di modifica nominativo, accessibile dai soli Clienti
class UpdatePurchaseView(GroupRequiredMixin, UserPassesTestMixin, UpdateView):
    group_required = ['Clienti']
    model = BigliettoAcquistato
    form_class = BigliettoAcquistatoCrispyForm
    template_name = "orders/edit_purchase.html"

    def dispatch(self, request, *args, **kwargs):
        # gestisce eventuali eccezioni Http404 che potrebbero essere sollevate durante il processo di elaborazione della richiesta
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return render(request, '404.html', status=404)

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        slug = self.kwargs.get('slug')
        pk = self.kwargs.get('pk')

        # trova l'oggetto utilizzando prima lo slug (tipologia del biglietto) e poi la pk (istanza del biglietto acquistato)
        biglietto_acquistato = get_object_or_404(queryset, pk=pk, biglietto__slug=slug)

        return biglietto_acquistato
    
    def test_func(self):
        user = self.request.user

        # verifica l'appartenenza al gruppo 'Clienti'
        if not user.groups.filter(name__in=self.group_required).exists():
            return False

        # verifica che l'utente corrente sia il proprietario del biglietto acquistato
        biglietto_acquistato = self.get_object()
        return biglietto_acquistato.ordine.utente == user.utente
    
    # se l'utente è autenticato ma non ha i permessi, solleva PermissionDenied
    def handle_no_permission(self):
        # in caso di tentato accesso ad una view protetta, senza i permessi adatti, reindirizza al login
        return redirect(f'{settings.LOGIN_URL}&next={self.request.path}')
    
    def form_valid(self, form):
        ticket = form.instance # recupero dell'istanza del modello attualmente utilizzata
        if ticket.can_edit():
            messages.success(self.request, f'{ticket.biglietto.tipologia} aggiornato con successo (ordine N.{ticket.ordine.id} - {ticket.data_acquisto.strftime("%d/%m/%Y")}).')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Non è più possibile effettuare il cambio per questo biglietto.')
            return redirect('users:profile')
        
    def get_success_url(self):
        return reverse_lazy('users:profile')