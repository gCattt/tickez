# apps/nome_app/tests.py

from django.test import TestCase, Client

from django.urls import reverse
from django.conf import settings
from django.contrib.messages import get_messages

from users.models import Utente, Organizzatore
from products.models import Evento
from common.models import Luogo
from django.contrib.auth.models import User, Group

from django.utils import timezone


class UpdateEventViewTest(TestCase):

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

        # creazione di User per gli Organizzatori di test
        self.user1_organizzatore = User.objects.create_user(username='testuser1_organizzatore', password='password123_organizzatore')
        group_organizzatori, created = Group.objects.get_or_create(name='Organizzatori')
        self.user1_organizzatore.groups.add(group_organizzatori)

        self.user2_organizzatore = User.objects.create_user(username='testuser2_organizzatore', password='password123_organizzatore')
        group_organizzatori, created = Group.objects.get_or_create(name='Organizzatori')
        self.user2_organizzatore.groups.add(group_organizzatori)

        self.organizzatore1 = Organizzatore.objects.create(
            nome='Organizzatore di Test 1',
            email='organizzatore1@test.com',
            user=self.user1_organizzatore
        )

        self.organizzatore2 = Organizzatore.objects.create(
            nome='Organizzatore di Test 2',
            email='organizzatore2@test.com',
            user=self.user2_organizzatore
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
            organizzatore=self.organizzatore2,
            luogo=self.luogo
        )

        self.client = Client()
        self.update_url = reverse('products:update-event', kwargs={'slug': self.evento.slug, 'pk': self.evento.pk})

    def test_view_uses_correct_template(self):
        self.client.login(username='testuser2_organizzatore', password='password123_organizzatore')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/update_entity.html')

    def test_event_not_found(self):
        self.client.login(username='testuser2_organizzatore', password='password123_organizzatore')
        invalid_url = reverse('products:update-event', kwargs={'slug': 'invalid-slug', 'pk': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.update_url)
        self.assertRedirects(response, f'{settings.LOGIN_URL}&next={self.update_url}')

    def test_access_denied_for_non_organizer(self):
        self.client.login(username='testuser_utente', password='password123_utente')
        response = self.client.get(self.update_url)
        self.assertRedirects(response, f'{settings.LOGIN_URL}&next={self.update_url}')

    def test_access_denied_for_non_owning_organizer(self):
        self.client.login(username='testuser1_organizzatore', password='password123_organizzatore')
        response = self.client.get(self.update_url)
        self.assertRedirects(response, f'{settings.LOGIN_URL}&next={self.update_url}')

    def test_access_template_for_owning_organizer(self):
        self.client.login(username='testuser2_organizzatore', password='password123_organizzatore')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/update_entity.html')

    def test_successful_event_update(self):
        self.client.login(username='testuser2_organizzatore', password='password123_organizzatore')
        post_data = {
            'nome': 'Updated Evento di Test',
            'categoria': 'Concerti',
            'data_ora': (timezone.now() + timezone.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'descrizione': 'Descrizione aggiornata',
            'luogo': self.luogo.pk
        }
        response = self.client.post(self.update_url, post_data)
        self.evento.refresh_from_db() # ricarica l'evento per ottenere il nuovo slug se cambiato
        self.assertRedirects(response, self.evento.get_absolute_url())
        self.assertEqual(self.evento.nome, 'Updated Evento di Test')
        self.assertEqual(self.evento.descrizione, 'Descrizione aggiornata')

    def test_invalid_event_update(self):
        self.client.login(username='testuser2_organizzatore', password='password123_organizzatore')
        post_data = {
            'nome': '',
            'categoria': 'Concerti',
            'data_ora': (timezone.now() + timezone.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'descrizione': 'Descrizione aggiornata',
            'luogo': self.luogo.pk
        }
        response = self.client.post(self.update_url, post_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('nome', form.errors)

    def test_overlapping_event_update(self):
        # creare un altro evento per l'organizzatore2 nello stesso giorno
        Evento.objects.create(
            nome='Another Evento',
            categoria='Concerti',
            data_ora=timezone.now() + timezone.timedelta(days=2),
            descrizione='Descrizione di test',
            organizzatore=self.organizzatore2,
            luogo=self.luogo
        )

        self.client.login(username='testuser2_organizzatore', password='password123_organizzatore')
        post_data = {
            'nome': 'Updated Evento di Test',
            'categoria': 'Concerti',
            'data_ora': (timezone.now() + timezone.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'descrizione': 'Descrizione aggiornata',
            'luogo': self.luogo.pk
        }
        response = self.client.post(self.update_url, post_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('data_ora', form.errors)

    def test_success_message_display(self):
        self.client.login(username='testuser2_organizzatore', password='password123_organizzatore')

        # Dati di aggiornamento dell'evento
        post_data = {
            'nome': 'Updated Evento di Test',
            'categoria': 'Concerti',
            'data_ora': (timezone.now() + timezone.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'descrizione': 'Descrizione aggiornata',
            'luogo': self.luogo.pk,
        }
        response = self.client.post(self.update_url, post_data)
        self.evento.refresh_from_db()  # ricarica l'evento per ottenere il nuovo slug se cambiato
        self.assertRedirects(response, self.evento.get_absolute_url())

        # Verifica che il messaggio di successo sia presente
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == 'Modifiche salvate con successo!' for msg in messages))
