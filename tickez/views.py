from django.http import HttpResponse

def home_page(request):
    return HttpResponse("Hello world! Questa è la home page.")