from django.http import HttpResponse
from django.shortcuts import render

def common(request):
    return HttpResponse("common test view.")
