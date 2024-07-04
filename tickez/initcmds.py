from common.models import Luogo, Notifica
from users.models import Organizzatore, Utente
from orders.models import Ordine
from products.models import Evento, Biglietto

from datetime import datetime, timedelta
import random
from django.contrib.auth.hashers import make_password

def erase_db():
    Luogo.objects.all().delete()
    Notifica.objects.all().delete()
    Utente.objects.all().delete()
    Ordine.objects.all().delete()
    Organizzatore.objects.all().delete()
    Evento.objects.all().delete()
    Biglietto.objects.all().delete()
    print("DB cancellato.")

def init_db():
    if len(Evento.objects.all())!=0:
        return
    
    luoghi = [
        {"nome": "Stadio Olimpico", "indirizzo": "Viale dei Gladiatori, Roma", "capienza_persone": 72698, "citta": "Roma", "stato": "Italia", "codice_postale": "00135"},
        {"nome": "Mediolanum Forum", "indirizzo": "Via G. Di Vittorio, Assago", "capienza_persone": 12700, "citta": "Milano", "stato": "Italia", "codice_postale": "20090"},
        {"nome": "Arena di Verona", "indirizzo": "Piazza Bra, Verona", "capienza_persone": 22000, "citta": "Verona", "stato": "Italia", "codice_postale": "37121"},
        {"nome": "Teatro La Fenice", "indirizzo": "Campo San Fantin, Venezia", "capienza_persone": 1000, "citta": "Venezia", "stato": "Italia", "codice_postale": "30124"},
        {"nome": "PalaAlpitour", "indirizzo": "Corso Sebastopoli, Torino", "capienza_persone": 15500, "citta": "Torino", "stato": "Italia", "codice_postale": "10134"}
    ]
    for luogo in luoghi:
        l = Luogo(**luogo)
        l.save()


    utenti = [
        {"username": "mario", "nome": "Mario", "cognome": "Rossi", "email": "mario.rossi@example.com", "data_nascita": "1980-05-15", "sesso": "M", "stato": "Italia", "indirizzo": "Via Roma 1, Milano", "telefono": "3456789012", "carta_credito": "1234567812345678", "cvv": "123", "scadenza_carta": "2025-06-30", "notifiche": False},
        {"username": "luigi", "nome": "Luigi", "cognome": "Verdi", "email": "luigi.verdi@example.com", "data_nascita": "1990-07-20", "sesso": "M", "stato": "Italia", "indirizzo": "Via Milano 2, Roma", "telefono": "3456789013", "carta_credito": "2345678923456789", "cvv": "234", "scadenza_carta": "2026-07-30", "notifiche": False},
        {"username": "giulia", "nome": "Giulia", "cognome": "Bianchi", "email": "giulia.bianchi@example.com", "data_nascita": "1985-03-10", "sesso": "F", "stato": "Italia", "indirizzo": "Via Torino 3, Firenze", "telefono": "3456789014", "carta_credito": "3456789034567890", "cvv": "345", "scadenza_carta": "2027-08-30", "notifiche": False},
        {"username": "francesca", "nome": "Francesca", "cognome": "Neri", "email": "francesca.neri@example.com", "data_nascita": "1995-12-25", "sesso": "F", "stato": "Italia", "indirizzo": "Via Napoli 4, Napoli", "telefono": "3456789015", "carta_credito": "4567890145678901", "cvv": "456", "scadenza_carta": "2028-09-30", "notifiche": False},
        {"username": "alessandro", "nome": "Alessandro", "cognome": "Gialli", "email": "alessandro.gialli@example.com", "data_nascita": "1975-08-05", "sesso": "M", "stato": "Italia", "indirizzo": "Via Firenze 5, Bologna", "telefono": "3456789016", "carta_credito": "5678901256789012", "cvv": "567", "scadenza_carta": "2029-10-30", "notifiche": False}
    ]
    for utente in utenti:
        password = make_password('default_password')
        utente_obj = Utente(username=utente['username'], password=password, **utente)
        utente_obj.save()


    organizzatori = [
        {"nome": "Adele", "descrizione": "Cantante britannica pop e soul", "notifiche": False},
        {"nome": "Ed Sheeran", "descrizione": "Cantautore britannico pop", "notifiche": False},
        {"nome": "Bruno Mars", "descrizione": "Cantautore e produttore statunitense", "notifiche": False},
        {"nome": "Beyoncé", "descrizione": "Cantante e attrice statunitense", "notifiche": False},
        {"nome": "Drake", "descrizione": "Rapper e cantante canadese", "notifiche": False}
    ]
    for organizzatore in organizzatori:
        o = Organizzatore(**organizzatore)
        o.save()


    luoghi = list(Luogo.objects.all())
    organizzatori = list(Organizzatore.objects.all())
    eventi = [
        {"nome": "Concerto di Capodanno", "descrizione": "Concerto speciale per celebrare il nuovo anno.", "data_ora": datetime.now() + timedelta(days=30), "categoria": "Concerti"},
        {"nome": "Festival Estivo", "descrizione": "Festival musicale estivo con vari artisti.", "data_ora": datetime.now() + timedelta(days=60), "categoria": "Festival"},
        {"nome": "Jazz Night", "descrizione": "Serata dedicata alla musica jazz.", "data_ora": datetime.now() + timedelta(days=90), "categoria": "Concerti"},
        {"nome": "Rock Fest", "descrizione": "Festival di musica rock con band internazionali.", "data_ora": datetime.now() + timedelta(days=120), "categoria": "Festival"},
        {"nome": "Classica sotto le stelle", "descrizione": "Concerto di musica classica", "data_ora": datetime.now() + timedelta(days=150), "categoria": "Teatro"}
    ]
    for evento in eventi:
        evento['luogo'] = random.choice(luoghi)
        evento['organizzatore'] = random.choice(organizzatori)
        e = Evento(**evento)
        e.save()


    eventi = list(Evento.objects.all())
    biglietti = [
        {"tipologia": "VIP", "prezzo": 150.00, "descrizione": "Biglietto VIP con accesso all'area riservata."},
        {"tipologia": "Standard", "prezzo": 50.00, "descrizione": "Biglietto standard con posto a sedere."},
        {"tipologia": "Economy", "prezzo": 30.00, "descrizione": "Biglietto economy con posto in piedi."},
        {"tipologia": "Premium", "prezzo": 100.00, "descrizione": "Biglietto premium con posto a sedere vicino al palco."},
        {"tipologia": "Backstage", "prezzo": 200.00, "descrizione": "Biglietto con accesso al backstage."}
    ]
    for biglietto in biglietti:
        biglietto['evento'] = random.choice(eventi)
        biglietto['organizzatore'] = random.choice(organizzatori)
        biglietto['quantita'] = random.randint(0, 100)
        b = Biglietto(**biglietto)
        b.save()


    print("DB popolato con successo.")