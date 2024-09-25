from django.shortcuts import render

from products.models import Evento
from orders.models import Ordine, BigliettoAcquistato

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


def home_page(request):
    home_page_events = Evento.objects.order_by('data_ora')[:5]
    templ = "common/home_page.html"
    ctx = {"object_list": home_page_events}

    # mostra gli eventi consigliati solo se l'utente è un cliente autenticato e facente parte del gruppo Clienti
    if request.user.is_authenticated and request.user.groups.filter(name='Clienti').exists():
        biglietti_acquistati = BigliettoAcquistato.objects.all()
        ordini_utente = Ordine.objects.filter(utente=request.user.utente)

        # gli utenti devono aver effettuato almeno un acquisto
        if ordini_utente.count() > 0:
            # dataframe con le informazioni rilevanti
            data = {
                'utente_id': [biglietto.ordine.utente.id for biglietto in biglietti_acquistati],
                'evento_id': [biglietto.biglietto.evento.id for biglietto in biglietti_acquistati]
            }
            df = pd.DataFrame(data)

            # matrice utente-elemento
            # l'argomento "aggfunc='size'" conta il numero di occorrenze di ciascuna combinazione di utente ed evento.
            user_event_matrix = df.pivot_table(index='utente_id', columns='evento_id', aggfunc='size', fill_value=0)

            # calcolo della somiglianza attraverso similarità del coseno tra gli utenti
            user_similarity = cosine_similarity(user_event_matrix)
            user_similarity_df = pd.DataFrame(user_similarity, index=user_event_matrix.index, columns=user_event_matrix.index)

            # restituisce i 5 elementi più affini
            def get_user_recommendations(utente_id, user_event_matrix, user_similarity_df, top_n=5):
                # ordina per somiglianza decrescente gli utenti (id), escluso se stesso, ottenendo così i più simili
                similar_users = user_similarity_df[utente_id].sort_values(ascending=False).index[1:]
                # ricava le similarità dagli id
                similarities = user_similarity_df.loc[utente_id, similar_users]

                # righe della matrice utente-elemento corrispondenti agli utenti nella lista 'similar_users', e quindi i loro eventi acquistati
                similar_users_events = user_event_matrix.loc[similar_users]

                # somma (lungo le righe) degli acquisti pesati per ottenere un punteggio di raccomandazione di ogni evento
                weighted_recommendations = (similar_users_events.T * similarities).T.sum()

                # serie contenente i punteggi di raccomandazione in ordine decrescente
                recommendations = weighted_recommendations.sort_values(ascending=False)

                # rimuove dagli elementi consigliati gli eventi che l'utente ha già acquistato
                user_events = user_event_matrix.loc[utente_id]
                recommendations = recommendations[user_events == 0] # utilizzo di una maschera booleana (seleziono gli elementi per cui è true)

                return recommendations.head(top_n).index
            
            # recupera gli eventi consigliati per l'utente
            utente_id = request.user.utente.id
            recommended_event_ids = get_user_recommendations(utente_id, user_event_matrix, user_similarity_df)
            recommended_events = Evento.objects.filter(id__in=recommended_event_ids)

            ctx['recommended_events'] = recommended_events

    return render(request, template_name=templ, context=ctx)


def custom_404_view(request):
    return render(request, '404.html', status=404)