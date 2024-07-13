import django_filters

from django import forms

from products.models import Evento


class EventoFilter(django_filters.FilterSet):
    SORT_CHOICES = (
        ('data_ora', 'Data ↑'),
        ('-data_ora', 'Data ↓'),
        ('nome', 'Nome (A-Z)'),
        ('-nome', 'Nome (Z-A)'),
    )
    sort = django_filters.ChoiceFilter(
        label='',
        choices=SORT_CHOICES,
        method='filter_by_sort',
        initial='data_ora',
        widget=forms.Select(attrs={
            'class': 'btn btn-outline-dark',
        }),
    )

    CATEGORY_CHOICES = Evento.CATEGORY_CHOICES
    category = django_filters.ChoiceFilter(
        field_name='categoria',
        label='',
        choices=CATEGORY_CHOICES,
        empty_label='Categoria',
        widget=forms.Select(attrs={
            'class': 'btn btn-outline-dark',
        }),
    )

    cities = Evento.objects.values_list('luogo__citta', flat=True).distinct().order_by('luogo__citta')
    CITY_CHOICES = [(city, city) for city in cities]
    city = django_filters.ChoiceFilter(
        field_name='luogo__citta',
        label='',
        choices=CITY_CHOICES,
        empty_label='Città',
        widget=forms.Select(attrs={
            'class': 'btn btn-outline-dark',
        }),
    )

    from_date = django_filters.DateFilter(
        field_name='data_ora',
        lookup_expr='gte',
        label='Da',
        widget=forms.DateInput(attrs={
            'id': 'from_date', # id utilizzato per datepicker
            'class': 'btn btn-sm btn-outline-dark',
        }),
    )

    until_date = django_filters.DateFilter(
        field_name='data_ora',
        lookup_expr='lte',
        label='A',
        widget=forms.DateInput(attrs={
            'id': 'until_date', # id utilizzato per datepicker
            'class': 'btn btn-sm btn-outline-dark',
        }),
    )

    def filter_by_sort(self, queryset, name, value):
        expression = {'data_ora': 'data_ora', '-data_ora': '-data_ora', 'nome': 'nome', '-nome': '-nome'}
        return queryset.order_by(expression[value])
    
    class Meta:
        model = Evento
        fields = ['sort', 'category', 'city', 'from_date', 'until_date']