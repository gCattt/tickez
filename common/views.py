from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.core.paginator import Paginator
from sellers.models import Evento
from datetime import datetime, timedelta


def common(request):
    #return HttpResponse("common test view.")
    return render(request, template_name="common/base_common.html")

class EventListView(ListView):
    model = Evento
    template_name = 'common/events.html' 
    paginate_by = 3

    def get_queryset(self):
        event_list = super().get_queryset()

        order_by = self.request.GET.get('sort', 'data_ora')
        event_list = self.order_style(event_list, order_by)

        city = self.request.GET.get('city', '')
        event_list = self.filter_by_city(event_list, city)

        category = self.request.GET.get('category', '')
        event_list = self.filter_by_category(event_list, category)

        from_date = self.request.GET.get('from_date', '')
        until_date = self.request.GET.get('until_date', '')
        event_list = self.filter_by_date(event_list, from_date, until_date)
        
        return event_list
    
    def order_style(self, queryset, order_by):
        if order_by == 'nome':
            return queryset.order_by('nome')
        else:
            return queryset.order_by('data_ora')

    def filter_by_city(self, queryset, city):
        if city:
            return queryset.filter(luogo__citta__icontains=city)
        return queryset

    def filter_by_category(self, queryset, category):
        if category:
            return queryset.filter(categoria=category)
        return queryset
    
    def filter_by_date(self, queryset, from_date, until_date):
        if from_date:
            queryset = queryset.filter(data_ora__gte=datetime.strptime(from_date, '%d/%m/%Y'))
        if until_date:
            queryset = queryset.filter(data_ora__lte=datetime.strptime(until_date, '%d/%m/%Y'))
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['events_number'] = self.get_queryset().count()

        context['current_sort'] = self.request.GET.get('sort', 'data_ora')
        context['current_city'] = self.request.GET.get('city', '')
        context['current_category'] = self.request.GET.get('category', '')

        context['cities'] = sorted(Evento.objects.values_list('luogo__citta', flat=True).distinct())
        context['categories'] = sorted(Evento.objects.values_list('categoria', flat=True).distinct())
        
        context['current_from'] = self.request.GET.get('from_date', '')
        context['current_until'] = self.request.GET.get('until_date', '')

        return context