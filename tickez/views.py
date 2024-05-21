from django.http import HttpResponse
from django.shortcuts import render
from sellers.models import Evento
from django.utils import timezone

def home_page(request):
    object_list_sorted = sorted(Evento.objects.all(), key=lambda x: abs(x.data_ora - timezone.now()))
    first_5_events = object_list_sorted[:5]

    templ = "common/home_page.html"
    ctx = {"title": "Tickez | Biglietti per Concerti, Festival e Teatro", 
           "object_list": first_5_events}
    return render(request, template_name=templ, context=ctx)