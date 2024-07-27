from .models import Notifica

# context processor utilizzato per fornire le notifiche dell'utente e il loro stato a tutti i template che richiedono questi dati.

# utilizzando @login_required, con un utente non autenticato otterrei un HttpResponseRedirect e non un dizionario vuoto
def notifications(request):
    notifications = []
    unread_count = 0

    if request.user.is_authenticated:
        # la funzionalità delle notifiche viene gestita solo per il model Utente
        try:
            utente = request.user.utente
            notifications = Notifica.objects.filter(
                organizzatore__in=utente.organizzatori_preferiti.all()
            ).order_by('-data_ora')
            unread_count = notifications.filter(letta=False).count()
        except:
            utente = None

    return {
        'notifications': notifications,
        'unread_count': unread_count,
    }