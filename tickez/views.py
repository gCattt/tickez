from django.shortcuts import render
from products.models import Evento

def home_page(request):
    home_page_events = Evento.objects.order_by('data_ora')[:5]

    templ = "common/home_page.html"
    ctx = {"object_list": home_page_events}

    return render(request, template_name=templ, context=ctx)