from django.contrib import admin
from .models import Ordine, BigliettoAcquistato

from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html


class OrdineAdmin(admin.ModelAdmin):
    model = Ordine

    readonly_fields = ('data_ora',)
    list_display = ('id', 'data_ora', 'totale', 'utente', 'organizzatore', 'evento', 'view_tickets_link')
    search_fields = ('id', 'utente__nome', 'utente__cognome', 'utente__user__username', 'utente__email', 'organizzatore__nome', 'evento__nome')
    list_filter = ('data_ora', 'organizzatore__nome', 'evento')
    
    fieldsets = (
        ('Details', {
            'fields': ('data_ora', 'totale')
        }),
        ('Associated', {
            'fields': ('utente', 'organizzatore', 'evento'),
            'classes': ('collapse',)  # mostra questi campi come nascosti per default
        }),
    )

    def view_tickets_link(self, obj):
        count = obj.biglietti_acquistati.count()
        url = (
            reverse("admin:orders_bigliettoacquistato_changelist")
            + "?"
            + urlencode({"ordine__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Biglietti Acquistati</a>', url, count)

    view_tickets_link.short_description = "Biglietti Acquistati"


class BigliettoAcquistatoAdmin(admin.ModelAdmin):
    model = BigliettoAcquistato

    readonly_fields = ('data_acquisto',)
    list_display = ('id', 'data_acquisto', 'biglietto_link', 'nome_acquirente', 'cognome_acquirente', 'data_nascita_acquirente', 'sesso_acquirente', 'stato_acquirente', 'prezzo_acquisto', 'ordine')
    search_fields = ('nome_acquirente', 'cognome_acquirente', 'ordine__utente__nome', 'ordine__utente__cognome', 'ordine__utente__user__username', 'ordine__utente__email', 'ordine__utente__user__username', 'biglietto__tipologia', 'biglietto__evento', 'ordine__id')
    list_filter = ('data_acquisto', 'sesso_acquirente', 'stato_acquirente', 'biglietto__evento')

    fieldsets = (
        ('Details', {
            'fields': ('biglietto', 'nome_acquirente', 'cognome_acquirente', 'data_acquisto', 'data_nascita_acquirente', 'sesso_acquirente', 'stato_acquirente', 'prezzo_acquisto')
        }),
        ('Associated', {
            'fields': ('ordine',),
            'classes': ('collapse',)  # mostra questi campi come nascosti per default
        }),
    )

    def biglietto_link(self, obj):
        name = obj.biglietto.tipologia
        url = (
            reverse("admin:products_biglietto_changelist")
            + "?"
            + urlencode({"id": f"{obj.biglietto.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, name)

    biglietto_link.short_description = "Biglietto"


admin.site.register(Ordine, OrdineAdmin)
admin.site.register(BigliettoAcquistato, BigliettoAcquistatoAdmin)