# apps/nome_app/tests.py

from django.test import TestCase

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings

from .models import Utente, Organizzatore
from products.models import Evento
from common.models import Luogo
from django.contrib.auth.models import User, Group

from django.utils import timezone


# funzionalità follow-unfollow
class ToggleFollowTestCase(TestCase):
    
    def setUp(self):
        # creazione di uno User per l'Utente di test
        self.user_utente = User.objects.create_user(username='testuser_utente', password='password123_utente')
        group_clienti, created = Group.objects.get_or_create(name='Clienti')
        self.user_utente.groups.add(group_clienti)
        # creazione di un Utente associato allo User appena creato
        self.utente = Utente.objects.create(
            user=self.user_utente,
            nome='Nome Utente',
            cognome='Cognome Utente',
            email='utente@example.com',
            data_nascita='2000-01-01'
        )

        # creazione di uno User per l'Organizzatore di test
        self.user_organizzatore = User.objects.create_user(username='testuser_organizzatore', password='password123_organizzatore')
        group_organizzatori, created = Group.objects.get_or_create(name='Organizzatori')
        self.user_organizzatore.groups.add(group_organizzatori)
        # creazione di un Organizzatore associato allo User appena creato
        self.organizzatore = Organizzatore.objects.create(
            nome='Organizzatore di Test',
            email='organizzatore@test.com',
            user=self.user_organizzatore
        )

        # creazione di un Luogo
        self.luogo = Luogo.objects.create(
            nome='Luogo di Test',
            indirizzo='Indirizzo di test',
            citta='Città di test',
            capienza_persone=100
        )

        # creazione di un Evento
        self.evento = Evento.objects.create(
            nome='Evento di Test',
            categoria='Concerti',
            data_ora=timezone.now() + timezone.timedelta(days=1),
            organizzatore=self.organizzatore,
            luogo=self.luogo
        )

    # azione 'follow' su un evento
    def test_toggle_follow_follow_action(self):
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['evento', self.evento.pk])
        response = self.client.post(url, {'action': 'follow'})
        
        # verifica che l'utente sia stato aggiunto come follower
        self.evento.refresh_from_db()
        self.assertIn(self.user_utente.utente, self.evento.followers.all())
        self.assertRedirects(response, self.evento.get_absolute_url())

    # azione 'unfollow' su un organizzatore
    def test_toggle_follow_unfollow_action(self):
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['organizzatore', self.organizzatore.pk])
        response = self.client.post(url, {'action': 'unfollow'})
        
        # verifica che l'utente sia stato rimosso dai follower
        self.organizzatore.refresh_from_db()
        self.assertNotIn(self.user_utente.utente, self.organizzatore.followers.all())
        self.assertRedirects(response, self.organizzatore.get_absolute_url())

    # azione sconosciuta
    def test_toggle_follow_unknown_action(self):
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['luogo', self.luogo.pk])
        response = self.client.post(url, {'action': 'unknown_action'})
        
        # verifica che non ci siano modifiche ai follower
        self.luogo.refresh_from_db()
        self.assertNotIn(self.user_utente.utente, self.luogo.followers.all())
        self.assertRedirects(response, self.luogo.get_absolute_url())

    # richiesta GET invece di POST
    def test_toggle_follow_get_request(self):
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['evento', self.evento.pk])
        response = self.client.get(url)
        
        # verifica che non ci siano modifiche ai follower
        self.evento.refresh_from_db()
        self.assertNotIn(self.user_utente.utente, self.evento.followers.all())
        self.assertRedirects(response, self.evento.get_absolute_url())

    # entity_type non supportato -> KeyError
    def test_toggle_follow_entity_type_not_supported(self):
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['manifestazione', '1'])
        response = self.client.post(url, {'action': 'follow'})
        
        # verifica che la risposta sia una pagina 404
        self.assertEqual(response.status_code, 404)

    # entity_pk non valido
    def test_toggle_follow_invalid_entity_pk(self):
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['evento', '999'])
        response = self.client.post(url, {'action': 'follow'})
        
        # verifica che la risposta sia una pagina 404
        self.assertEqual(response.status_code, 404)

    # utente non autenticato
    def test_toggle_follow_unauthenticated_user(self):
        url = reverse('users:toggle-follow', args=['evento', self.evento.pk])
        response = self.client.post(url, {'action': 'follow'})
        
        # verifica reindirizzamento a pagina di accesso non autorizzato
        self.assertRedirects(response, f'{settings.LOGIN_URL}&next={url}')

    # utente che non è un cliente
    def test_toggle_follow_user_not_customer(self):
        self.user_utente.groups.clear()  # rimuove l'utente dal gruppo "Clienti"
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['evento', self.evento.pk])
        response = self.client.post(url, {'action': 'follow'})
        
        # verifica che non ci siano modifiche ai follower
        self.evento.refresh_from_db()
        self.assertNotIn(self.user_utente.utente, self.evento.followers.all())
        
        # verifica reindirizzamento a pagina di accesso non autorizzato
        self.assertRedirects(response, f'{settings.LOGIN_URL}&next={url}')

    # decoratore is_customer
    def test_toggle_follow_is_customer_decorator(self):
        self.client.force_login(self.user_utente)
        url = reverse('users:toggle-follow', args=['evento', self.evento.pk])
        response = self.client.post(url, {'action': 'follow'})
        
        # verifica che l'utente possa eseguire l'azione se è un cliente
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user_utente.utente, self.evento.followers.all())
        self.assertRedirects(response, self.evento.get_absolute_url())

    # consistenza architetturale
    def test_toggle_follow_architectural_consistency(self):
        self.client.force_login(self.user_utente)
        
        entities = [
            ('evento', self.evento.pk),
            ('organizzatore', self.organizzatore.pk),
            ('luogo', self.luogo.pk),
        ]
        
        # azione 'follow' sulle varie entità
        for entity_type, entity_pk in entities:
            url = reverse('users:toggle-follow', args=[entity_type, entity_pk])
            response = self.client.post(url, {'action': 'follow'})
            
            entity = get_object_or_404({
                'evento': Evento,
                'organizzatore': Organizzatore,
                'luogo': Luogo,
            }[entity_type], pk=entity_pk)

            self.assertRedirects(response, entity.get_absolute_url())
            self.assertIn(self.user_utente.utente, entity.followers.all())

        # azione 'unfollow' sulle varie entità
        for entity_type, entity_pk in entities:
            url = reverse('users:toggle-follow', args=[entity_type, entity_pk])
            response = self.client.post(url, {'action': 'unfollow'})

            entity = get_object_or_404({
                'evento': Evento,
                'organizzatore': Organizzatore,
                'luogo': Luogo,
            }[entity_type], pk=entity_pk)

            self.assertRedirects(response, entity.get_absolute_url())
            self.assertNotIn(self.user_utente.utente, entity.followers.all())