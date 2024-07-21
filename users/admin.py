from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from .models import Utente, Organizzatore

from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html


class UtenteInline(admin.StackedInline):
    model = Utente
    can_delete = False
    verbose_name = 'Additional information'
    readonly_fields = ('nome', 'cognome', 'email', 'data_nascita', 'sesso', 'stato', 'telefono', 'immagine_profilo')

class OrganizzatoreInline(admin.StackedInline):
    model = Organizzatore
    can_delete = False
    verbose_name = 'Additional Information'
    readonly_fields = ('nome', 'slug', 'descrizione', 'immagine_profilo', 'followers')

class CustomUserAdmin(UserAdmin):
    readonly_fields = ('first_name', 'last_name', 'email')
    # campi visualizzati nel modulo di modifica dell'utente nel pannello di amministrazione
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
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if hasattr(obj, 'utente'):
            return [UtenteInline(self.model, self.admin_site)]
        elif hasattr(obj, 'organizzatore'):
            return [OrganizzatoreInline(self.model, self.admin_site)]
        return []

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


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