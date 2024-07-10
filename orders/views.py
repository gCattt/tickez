from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CheckoutCrispyForm, BigliettoAcquistatoCrispyForm

from .models import Ordine, BigliettoAcquistato
from products.models import Biglietto
from users.models import Utente, Organizzatore

from django.views.generic import UpdateView

from django.contrib import messages

from django.utils import timezone


def orders(request):
    return render(request, template_name="orders/base_orders.html")


@login_required
def checkout(request):
    if request.method == 'POST':
        selected_tickets = []
        total = 0

        # recupera i biglietti selezionati
        for key, value in request.POST.items():
            if key.startswith("quantita_") and int(value) > 0:
                ticket_id = key.split("_")[1]
                biglietto = Biglietto.objects.get(id=ticket_id)
                quantity = int(value)
                for _ in range(quantity):
                    selected_tickets.append(biglietto)
                    total += biglietto.prezzo

        # memorizza i biglietti selezionati nella sessione (gli ID in quanto l'oggetto Biglietto non è serializzabile)
        request.session['selected_tickets'] = [t.id for t in selected_tickets]
        request.session['total'] = total
        
        form = CheckoutCrispyForm()
        return render(request, 'orders/checkout.html', {
            'selected_tickets': selected_tickets,
            'total': total,
            'form': form
        })

    return redirect('homepage')

@login_required
def process_payment(request):
    if request.method == 'POST':
        selected_tickets = request.session.get('selected_tickets', [])
        total = request.session.get('total', 0)
        
        # ottieni l'istanza di Utente associata all'utente autenticato
        try:
            utente = Utente.objects.get(user=request.user)
        except Utente.DoesNotExist:
            messages.error(request, 'Utente non trovato.')
            return redirect('homepage')
        
        # ottieni l'organizzatore che ha creato i biglietti (basta il primo)
        if selected_tickets:
            organizzatore = Biglietto.objects.get(id=selected_tickets[0]).organizzatore
        else:
            messages.error(request, 'Nessun biglietto selezionato.')
            return redirect('homepage')
        
        ordine = Ordine.objects.create(
            utente=utente,
            organizzatore=organizzatore,
            totale=total,
            data_ora=timezone.now()
        )
        
        # aggiorna la quantità dei biglietti e associa i biglietti all'ordine appena creato
        for ticket_id in selected_tickets:
            biglietto = Biglietto.objects.get(id=ticket_id)
            
            biglietto.quantita -= 1
            biglietto.save()
        
            BigliettoAcquistato.objects.create(
                biglietto=biglietto,
                ordine=ordine,
                nome_acquirente=utente.nome,
                cognome_acquirente=utente.cognome,
                data_acquisto=timezone.now()
            )
        
        messages.success(request, 'L\'ordine è stato effettuato con successo!')
        return redirect('users:profile')
    
    return redirect('homepage')  # reindirizza alla homepage se non è un POST


class UpdatePurchaseView(LoginRequiredMixin, UpdateView):
    model = BigliettoAcquistato
    form_class = BigliettoAcquistatoCrispyForm
    template_name = "orders/edit_purchase.html"

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        slug = self.kwargs.get('slug')
        pk = self.kwargs.get('pk')

        # trova l'oggetto utilizzando prima lo slug (tipologia del biglietto) e poi la pk (istanza del biglietto acquistato)
        biglietto = get_object_or_404(Biglietto, slug=slug)
        return get_object_or_404(queryset, pk=pk, biglietto=biglietto)

    def get_success_url(self):
        return reverse_lazy('users:profile')
    
    def form_valid(self, form):
        ticket = form.instance
        if ticket.can_edit():
            messages.success(self.request, f'{ticket.biglietto.tipologia} (ordine N.{ticket.ordine.id}) aggiornato con successo.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Non è più possibile effettuare il cambio per questo biglietto.')
            return redirect('users:profile')