from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from users.models import Utente, Organizzatore

def users(request):
    return render(request, template_name="users/base_users.html")

class ArtistsListView(ListView):
    model = Organizzatore
    template_name = 'users/artists.html' 
    paginate_by = 3

    def get_queryset(self):
        artist_list = super().get_queryset()
        
        return artist_list.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class ArtistDetailView(DetailView):
    model = Organizzatore
    template_name = "users/artist_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.get_object().nome
        context['planned_events'] = self.get_object().eventi_organizzati.all()

        return context