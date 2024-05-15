from django.http import HttpResponse
from django.shortcuts import render

def customers(request):
    return HttpResponse("customers test view.")

