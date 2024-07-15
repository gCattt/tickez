from django.shortcuts import render

from products.models import Evento

from orders.models import Ordine, BigliettoAcquistato

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


def home_page(request):
    home_page_events = Evento.objects.order_by('data_ora')[:5]
    templ = "common/home_page.html"
    ctx = {"object_list": home_page_events}

    # mostra i consigliati solo se l'utente è un cliente autenticato e facente parte del gruppo Clienti
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

            user_event_matrix = df.pivot_table(index='utente_id', columns='evento_id', aggfunc='size', fill_value=0)

            # similarità del coseno tra gli utenti
            user_similarity = cosine_similarity(user_event_matrix)
            user_similarity_df = pd.DataFrame(user_similarity, index=user_event_matrix.index, columns=user_event_matrix.index)

            def get_user_recommendations(utente_id, user_event_matrix, user_similarity_df, top_n=5):
                # trova gli utenti più simili (escluso se stesso)
                similar_users = user_similarity_df[utente_id].sort_values(ascending=False).index[1:]

                # trova gli eventi acquistati dagli utenti simili
                similar_users_events = user_event_matrix.loc[similar_users]

                # somma le interazioni degli utenti simili per ottenere un punteggio di raccomandazione
                recommendations = similar_users_events.sum(axis=0).sort_values(ascending=False)

                # rimuove gli eventi che l'utente ha già acquistato
                user_events = user_event_matrix.loc[utente_id]
                recommendations = recommendations[user_events == 0]

                return recommendations.head(top_n).index
            
            # id dell'utente loggato
            utente_id = request.user.utente.id

            # recupera gli eventi consigliati per l'utente
            recommended_event_ids = get_user_recommendations(utente_id, user_event_matrix, user_similarity_df)
            recommended_events = Evento.objects.filter(id__in=recommended_event_ids)

            ctx['recommended_events'] = recommended_events

    return render(request, template_name=templ, context=ctx)