from django.shortcuts import render, redirect

from .forms import CheckoutForm

from .models import Ordine
from products.models import Biglietto
from users.models import Utente, Organizzatore

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.utils import timezone


def orders(request):
    return render(request, template_name="orders/base_orders.html")


@login_required
def checkout(request):
    if request.method == 'POST':
        selected_tickets = []
        totale = 0

        # recupera i biglietti selezionati
        for key, value in request.POST.items():
            if key.startswith("quantita_") and int(value) > 0:
                ticket_id = key.split("_")[1]
                biglietto = Biglietto.objects.get(id=ticket_id)
                quantita = int(value)

                selected_tickets.append({"biglietto": biglietto, "quantita": quantita})
                totale += biglietto.prezzo * quantita

        # memorizza i biglietti selezionati nella sessione
        request.session['selected_tickets'] = [
            {"biglietto_id": item["biglietto"].id, "quantita": item["quantita"]}
            for item in selected_tickets
        ]
        request.session['totale'] = totale
        
        form = CheckoutForm()
        return render(request, 'orders/checkout.html', {
            'selected_tickets': selected_tickets,
            'totale': totale,
            'form': form
        })

    return redirect('homepage')

@login_required
def process_payment(request):
    if request.method == 'POST':
        selected_tickets = request.session.get('selected_tickets', [])
        totale = request.session.get('totale', 0)
        
        # ottieni l'istanza di Utente associata all'utente autenticato
        try:
            utente = Utente.objects.get(user=request.user)
        except Utente.DoesNotExist:
            messages.error(request, 'Utente non trovato.')
            return redirect('homepage')
        
        # ottieni l'organizzatore che ha creato i biglietti
        if selected_tickets:
            primo_biglietto = Biglietto.objects.get(id=selected_tickets[0]['biglietto_id'])
            organizzatore = primo_biglietto.organizzatore
        else:
            messages.error(request, 'Nessun biglietto selezionato.')
            return redirect('homepage')
        
        ordine = Ordine.objects.create(
            utente=utente,
            organizzatore=organizzatore,
            totale=totale,
            data_ora=timezone.now()
        )
        
        # aggiorna la quantità dei biglietti e associa i biglietti all'ordine appena creato
        for item in selected_tickets:
            biglietto = Biglietto.objects.get(id=item['biglietto_id'])
            quantita = item['quantita']
            
            biglietto.quantita -= quantita
            biglietto.save()

            ordine.biglietti.add(biglietto)
        
        messages.success(request, 'Il pagamento è stato effettuato con successo!')
        return redirect('users:profile')
    
    return redirect('homepage')  # reindirizza alla homepage se non è un POST