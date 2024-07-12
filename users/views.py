from django.shortcuts import render
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, DetailView, UpdateView

from django.contrib.auth.models import User
from users.models import Organizzatore

from .forms import *


def users(request):
    return render(request, template_name="users/base_users.html")


class AdminProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/admin_profile.html'
    success_url = reverse_lazy('users:admin-profile')

    def get_object(self, queryset=None):
        return self.request.user

class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        if hasattr(self.request.user, 'organizzatore'):
            return self.request.user.organizzatore
        else:
            return self.request.user.utente

    def get_form_class(self):
        if hasattr(self.request.user, 'organizzatore'):
            return OrganizzatoreEditCrispyForm
        else:
            return CustomerEditCrispyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'organizzatore'):
            organizzatore = self.get_object()
            context['is_organizer'] = True
            context['user'] = self.request.user
            context['immagine_profilo'] = organizzatore.immagine_profilo_url
            context['orders'] = organizzatore.ordini.all()
            context['events'] = organizzatore.eventi_organizzati.all()
        else:
            utente = self.get_object()
            context['is_organizer'] = False
            context['user'] = self.request.user
            context['immagine_profilo'] = utente.immagine_profilo_url
            context['orders'] = utente.ordini.all()
            context['starred_events'] = utente.eventi_preferiti.all()
            context['starred_artists'] = utente.organizzatori_preferiti.all()
            context['starred_locations'] = utente.luoghi_preferiti.all()
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    

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