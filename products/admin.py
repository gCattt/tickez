from django.contrib import admin
from .models import Evento, Biglietto

from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html


# personalizzazione dell'interfaccia di amministrazione per il model Evento
class EventoAdmin(admin.ModelAdmin):
    model = Evento

    readonly_fields = ('slug', 'visualizzazioni')
    list_display = ('nome', 'categoria', 'data_ora', 'organizzatore_link', 'luogo_link', 'descrizione', 'visualizzazioni')
    search_fields = ('nome', 'categoria', 'organizzatore__nome', 'luogo__nome', 'descrizione')
    list_filter = ('categoria', 'data_ora', 'organizzatore__nome', 'luogo__nome')
    filter_horizontal = ('followers',)

    fieldsets = (
        ('Details', {
            'fields': ('organizzatore', 'luogo', 'nome', 'slug', 'categoria', 'data_ora', 'locandina', 'descrizione')
        }),
        ('Statistics', {
            'fields': ('visualizzazioni',)
        }),
        ('Associated', {
            'fields': ('followers',),
            'classes': ('collapse',)
        }),
    )

    # funzione per creare un link all'organizzatore di un dato evento
    def organizzatore_link(self, obj):
        name = obj.organizzatore
        url = (
            reverse("admin:users_organizzatore_changelist")
            + "?"
            + urlencode({"id": f"{obj.organizzatore.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, name)

    organizzatore_link.short_description = "Organizzatore"

    # funzione per creare un link al luogo in cui si svolge un dato evento
    def luogo_link(self, obj):
        name = obj.luogo.nome
        url = (
            reverse("admin:common_luogo_changelist")
            + "?"
            + urlencode({"id": f"{obj.luogo.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, name)

    luogo_link.short_description = "Luogo"


# personalizzazione dell'interfaccia di amministrazione per il model Biglietto
class BigliettoAdmin(admin.ModelAdmin):
    model = Biglietto

    readonly_fields = ('slug',)
    list_display = ('tipologia', 'evento_link', 'prezzo',  'quantita_vendibile', 'quantita')
    search_fields = ('tipologia', 'descrizione', 'evento__nome', 'organizzatore__nome')
    list_filter = ('evento', 'organizzatore__nome', 'prezzo')

    fieldsets = (
        ('Details', {
            'fields': ('tipologia', 'slug', 'prezzo', 'quantita', 'quantita_vendibile', 'descrizione')
        }),
        ('Associated', {
            'fields': ('evento', 'organizzatore'),
            'classes': ('collapse',)  # mostra questa sezione come nascosta per default
        }),
    )

    # funzione per creare un link all'evento di riferimento di un dato biglietto
    def evento_link(self, obj):
        name = obj.evento.nome
        url = (
            reverse("admin:products_evento_changelist")
            + "?"
            + urlencode({"id": f"{obj.evento.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, name)

    evento_link.short_description = "Evento"


admin.site.register(Evento, EventoAdmin)
admin.site.register(Biglietto, BigliettoAdmin)