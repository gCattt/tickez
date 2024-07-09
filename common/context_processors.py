from .models import Notifica


# utilizzando @login_required, con un utente non autenticato otterrei un HttpResponseRedirect e non un dizionario vuoto
def notifications(request):
    notifications = []
    unread_count = 0

    if request.user.is_authenticated:
        try:
            utente = request.user.utente
            notifications = Notifica.objects.filter(organizzatore__in=utente.organizzatori_preferiti.all()).order_by('-data_ora')
            unread_count = notifications.filter(letta=False).count()
        except:
            utente = None

    return {
        'notifications': notifications,
        'unread_count': unread_count,
    }