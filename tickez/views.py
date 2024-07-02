from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib import messages

from products.models import Evento

#from .forms import *

def home_page(request):
    home_page_events = Evento.objects.order_by('data_ora')[:5]

    templ = "common/home_page.html"
    ctx = {"object_list": home_page_events}

    return render(request, template_name=templ, context=ctx)


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.success(request, ("Si è verificato un errore. Riprova"))
            return redirect('login')
            
    else:
        return render(request, 'registration/login.html', {})