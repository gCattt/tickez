from common.models import Luogo, Notifica
from users.models import Organizzatore, Utente
from orders.models import Ordine, BigliettoAcquistato
from products.models import Evento, Biglietto
from django.contrib.auth.models import User, Group

from django.conf import settings

from django.db import connection

from datetime import datetime, timedelta
from django.utils import timezone
import sys, os, json, random


# totale eliminazione dei dati 
def erase_db():
    # salta l'inizializzazione se si stanno eseguendo i test
    if 'test' in sys.argv:
        return
    
    Luogo.objects.all().delete()
    Notifica.objects.all().delete()
    Organizzatore.objects.all().delete()
    Utente.objects.all().delete()
    Ordine.objects.all().delete()
    BigliettoAcquistato.objects.all().delete()
    Evento.objects.all().delete()
    Biglietto.objects.all().delete()
    User.objects.all().delete()

    print("DB cancellato correttamente.\n")


# resetta l'id counter delle tabelle
def reset_ids(tables):
	for t in tables:
		with connection.cursor() as cursor:
			cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{t}';")

# definizione degli utenti dell'applicazione
def init_users():
    # superuser
    admin = User.objects.create_superuser(username="admin", password="password")
    admin.save()
    # creazione dei gruppi
    clienti_group, created = Group.objects.get_or_create(name='Clienti')
    organizzatori_group, created = Group.objects.get_or_create(name='Organizzatori')

    # clienti
    clienti_file = os.path.join(settings.BASE_DIR, 'static', 'json', 'users.json')
    with open(clienti_file, 'r', encoding='utf-8') as f:
        clienti_data = json.load(f)

        for cliente_data in clienti_data:
            username = cliente_data['username']
            password = cliente_data.get('password', 'utentepw')
            utente = User.objects.create_user(username=username, password=password)
            cliente = Utente.objects.create(
                nome=cliente_data['nome'],
                cognome=cliente_data['cognome'],
                email=cliente_data['email'],
                data_nascita=cliente_data['data_nascita'],
                sesso=cliente_data['sesso'],
                stato=cliente_data['stato'],
                telefono=cliente_data.get('telefono', None),
                user=utente
            )
            clienti_group.user_set.add(utente)
            cliente.save()

        # organizzatori
        organizzatori_file = os.path.join(settings.BASE_DIR, 'static', 'json', 'organizers.json')
        with open(organizzatori_file, 'r', encoding='utf-8') as f:
            organizzatori_data = json.load(f)

        for organizzatore_data in organizzatori_data:
            username = organizzatore_data['username']
            password = organizzatore_data.get('password', 'organizzatorepw')
            utente = User.objects.create_user(username=username, password=password)
            organizzatore = Organizzatore.objects.create(
                nome=organizzatore_data['nome'],
                email=organizzatore_data['email'],
                descrizione=organizzatore_data.get('descrizione', ''),
                immagine_profilo=organizzatore_data.get('immagine_profilo', ''),
                user=utente
            )
            organizzatori_group.user_set.add(utente)
            organizzatore.save()

    print("Utenti creati con successo.\n")

# definizione dei luoghi
def init_venues():
    venues_file = os.path.join(settings.BASE_DIR, 'static', 'json', 'venues.json')

    with open(venues_file, 'r', encoding='utf-8') as f:
        venues_data = json.load(f)

        for venue_data in venues_data:
            nome = venue_data['nome']
            indirizzo = venue_data['indirizzo']
            citta = venue_data['citta']
            capienza_persone = venue_data['capienza_persone']
            immagine_path = venue_data['immagine']

            # verifica se il luogo già esiste
            if Luogo.objects.filter(nome=nome).exists():
                continue

            # Crea e salva il luogo
            luogo = Luogo(
                nome=nome,
                indirizzo=indirizzo,
                citta=citta,
                capienza_persone=capienza_persone,
                immagine=immagine_path
            )
            luogo.save()

    print("Luoghi creati con successo.\n")

# definizione degli eventi
def init_events():
    events_file = os.path.join(settings.BASE_DIR, 'static', 'json', 'events.json')

    with open(events_file, 'r', encoding='utf-8') as f:
        events_data = json.load(f)

        for event_data in events_data:
            nome = event_data['nome']
            categoria = event_data['categoria']
            locandina = event_data['locandina']
            descrizione = event_data['descrizione']
            organizzatore = event_data['organizzatore']
            luogo = event_data['luogo']

            try:
                organizzatore = Organizzatore.objects.get(slug=organizzatore)
            except Organizzatore.DoesNotExist:
                print(f"Organizzatore con slug '{organizzatore}' non trovato. Evento '{nome}' non creato.")
                continue

            try:
                luogo = Luogo.objects.get(slug=luogo)
            except Luogo.DoesNotExist:
                print(f"Luogo con nome '{luogo}' non trovato. Evento '{nome}' non creato.")
                continue

            data_ora = timezone.now() + timedelta(seconds=random.randint(0, int(((timezone.now() + timedelta(days=2*365)) - timezone.now()).total_seconds())))
            data_ora = data_ora.replace(hour=random.randint(18, 19), minute=00, second=0, microsecond=0)
            evento = Evento.objects.create(
                nome=nome,
                categoria=categoria,
                data_ora=data_ora,
                locandina=locandina,
                descrizione=descrizione,
                visualizzazioni=random.randint(0, 500),
                organizzatore=organizzatore,
                luogo=luogo
            )
            evento.save()

    print(f"Eventi creati con successo.\n")

# definizione delle tipologie di biglietti
def init_tickets():
    tickets_file = os.path.join(settings.BASE_DIR, 'static', 'json', 'tickets.json')

    with open(tickets_file, 'r') as f:
        tickets_data = json.load(f)
        
        for ticket_data in tickets_data:
            tipologia = ticket_data['tipologia']
            prezzo = ticket_data['prezzo']
            quantita = ticket_data['quantita']
            descrizione = ticket_data['descrizione']
            evento = ticket_data['evento']
            
            try:
                evento = Evento.objects.get(slug=evento)
            except Evento.DoesNotExist:
                print(f"Evento con slug '{evento}' non trovato. Biglietto '{tipologia}' non creato.")
                continue

            Biglietto.objects.create(
                tipologia=tipologia,
                prezzo=prezzo,
                quantita=quantita,
                quantita_vendibile=quantita,
                descrizione=descrizione,
                evento=evento,
                organizzatore=evento.organizzatore
            )
        
    print(f"Biglietti creati con successo.\n")

# definizione ordini
def init_orders():
    for _ in range(10):
        utente = random.choice(Utente.objects.all())
        biglietto = random.choice(Biglietto.objects.all())
        evento = biglietto.evento
        organizzatore = biglietto.organizzatore

        total = biglietto.prezzo

        random_datetime = timezone.now() + timedelta(hours=random.randint(1, 5))
        # Crea l'ordine
        ordine = Ordine.objects.create(
            utente=utente,
            organizzatore=organizzatore,
            evento=evento,
            totale=total,
            data_ora=random_datetime
        )

        # Crea un BigliettoAcquistato per l'ordine
        BigliettoAcquistato.objects.create(
            biglietto=biglietto,
            ordine=ordine,
            nome_acquirente=utente.nome,
            cognome_acquirente=utente.cognome,
            data_nascita_acquirente=utente.data_nascita,
            sesso_acquirente=utente.sesso,
            stato_acquirente=utente.stato,
            data_acquisto=random_datetime,
            prezzo_acquisto=biglietto.prezzo
        )

    print(f"Ordini creati con successo.\n")

# definizione dati iniziali del database
def init_db():
    # salta l'inizializzazione se si stanno eseguendo i test
    if 'test' in sys.argv:
        return
    
    tables=["auth_user","auth_user_groups","auth_group","users_organizzatore","users_utente","common_luogo","common_notifica","products_evento","products_biglietto","orders_ordine","orders_bigliettoacquistato"]
    reset_ids(tables)

    if Evento.objects.count()!= 0:
        return
    
    init_users()
    init_venues()
    init_events()
    init_tickets()
    init_orders()

    print("DB popolato correttamente.\n")