from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from .models import Utente, Organizzatore

from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html


# inline per visualizzare informazioni aggiuntive su Utente all'interno del pannello di amministrazione del model User
class UtenteInline(admin.StackedInline):
    model = Utente
    can_delete = False
    verbose_name = 'Additional information'
    readonly_fields = ('nome', 'cognome', 'email', 'data_nascita', 'sesso', 'stato', 'telefono', 'immagine_profilo')

# inline per visualizzare informazioni aggiuntive su Organizzatore all'interno del pannello di amministrazione del model User
class OrganizzatoreInline(admin.StackedInline):
    model = Organizzatore
    can_delete = False
    verbose_name = 'Additional Information'
    readonly_fields = ('nome', 'slug', 'descrizione', 'immagine_profilo', 'followers')

# personalizzazione dell'interfaccia di amministrazione per i model Utente ed Organizzatore
class CustomUserAdmin(UserAdmin):
    readonly_fields = ('first_name', 'last_name', 'email')
    # campi visualizzati nel modulo di modifica nel pannello di amministrazione
    fieldsets = (
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'username', 'email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # definizione dell'inline da mostrare sulla base del modello considerato
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if hasattr(obj, 'utente'):
            return [UtenteInline(self.model, self.admin_site)]
        elif hasattr(obj, 'organizzatore'):
            return [OrganizzatoreInline(self.model, self.admin_site)]
        return []

# l'implementazione predefinita dell'amministratore per il model User viene sostituita
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# personalizzazione dell'interfaccia di amministrazione per il model Utente
class UtenteAdmin(admin.ModelAdmin):
    model = Utente

    readonly_fields = ('user',)
    list_display = ('user', 'email', 'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'telefono')
    search_fields = ('user', 'email', 'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'telefono')
    list_filter = ('sesso', 'stato')

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Personal info', {
            'fields': ('nome', 'cognome', 'email', 'data_nascita', 'sesso', 'immagine_profilo')
        }),
        ('Contacts', {
            'fields': ('stato', 'telefono')
        })
    )


# personalizzazione dell'interfaccia di amministrazione per il model Organizzatore
class OrganizzatoreAdmin(admin.ModelAdmin):
    model = Organizzatore

    readonly_fields = ('user', 'slug')
    list_display = ('user', 'nome', 'email', 'descrizione', 'evento_link')
    search_fields = ('user', 'nome', 'email', 'descrizione')
    filter_horizontal = ('followers',)

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Personal info', {
            'fields': ('nome', 'slug', 'email', 'immagine_profilo', 'descrizione')
        }),
        ('Associated', {
            'fields': ('followers',),
            'classes': ('collapse',)  # mostra questa sezione come nascosta per default
        }),
    )

    # funzione per creare un link alla lista di eventi organizzati per un dato organizzatore (identificato da uno specifico id)
    def evento_link(self, obj):
        count = obj.eventi_organizzati.count()
        url = (
            reverse("admin:products_evento_changelist")
            + "?"
            + urlencode({"organizzatore__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Eventi Organizzati</a>', url, count)

    evento_link.short_description = "Eventi Organizzati"


admin.site.register(Utente, UtenteAdmin)
admin.site.register(Organizzatore, OrganizzatoreAdmin)