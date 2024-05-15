from django.http import HttpResponse
from django.shortcuts import render

def orders(request):
    return HttpResponse("orders test view.")


