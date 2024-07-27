from django.contrib import admin
from .models import Luogo, Notifica

from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html


# personalizzazione dell'interfaccia di amministrazione per il model Luogo
class LuogoAdmin(admin.ModelAdmin):
    model = Luogo
    
    readonly_fields = ('slug',)
    list_display = ('nome', 'citta', 'capienza_persone', 'evento_link')
    search_fields = ('nome', 'indirizzo', 'citta')
    list_filter = ('citta',)
    filter_horizontal = ('followers', 'affittuari')

    fieldsets = (
        ('Details', {
            'fields': ('nome', 'slug', 'indirizzo', 'citta', 'capienza_persone', 'immagine')
        }),
        ('Associated', {
            'fields': ('followers', 'affittuari'),
            'classes': ('collapse',)  # mostra questi campi come nascosti per default
        }),
    )

    # funzione per creare un link alla lista di eventi programmati per un dato luogo (identificato da uno specifico id)
    def evento_link(self, obj):
        count = obj.eventi_programmati.count()
        url = (
            reverse("admin:products_evento_changelist")
            + "?"
            + urlencode({"luogo__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Eventi Programmati</a>', url, count)

    evento_link.short_description = "Eventi Programmati"


# personalizzazione dell'interfaccia di amministrazione per il model Notifica
class NotificaAdmin(admin.ModelAdmin):
    model = Notifica

    readonly_fields = ('data_ora',)
    list_display = ('testo', 'data_ora', 'letta', 'evento', 'organizzatore', 'luogo')
    search_fields = ('testo', 'evento__nome', 'organizzatore__nome', 'luogo__nome')
    list_filter = ('letta', 'data_ora', 'organizzatore__nome', 'luogo__nome')
    
    fieldsets = (
        ('Details', {
            'fields': ('testo', 'data_ora', 'letta')
        }),
        ('Associated', {
            'fields': ('ordine', 'evento', 'organizzatore', 'luogo'),
        }),
    )


admin.site.register(Luogo, LuogoAdmin)
admin.site.register(Notifica, NotificaAdmin)