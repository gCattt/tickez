from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from .models import Utente, Organizzatore


class UtenteInline(admin.StackedInline):
    model = Utente
    can_delete = False
    verbose_name = 'Additional information'
    readonly_fields = ('nome', 'cognome', 'email', 'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono', 'carta_credito', 'cvv', 'scadenza_carta', 'notifiche')

class OrganizzatoreInline(admin.StackedInline):
    model = Organizzatore
    can_delete = False
    verbose_name = 'Additional Information'
    readonly_fields = ('nome', 'slug', 'descrizione', 'notifiche', 'followers')

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

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Personal info', {
            'fields': ('nome', 'cognome', 'email', 'data_nascita', 'sesso', 'notifiche')
        }),
        ('Contacts', {
            'fields': ('stato', 'indirizzo', 'telefono')
        }),
        ('Card info', {
            'fields': ('carta_credito', 'cvv', 'scadenza_carta')
        }),
    )

    list_display = ('user', 'email', 'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono')
    search_fields = ('user', 'email', 'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono')

class OrganizzatoreAdmin(admin.ModelAdmin):
    model = Organizzatore

    readonly_fields = ('user', 'slug')
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Personal info', {
            'fields': ('nome', 'slug', 'email', 'descrizione', 'notifiche', 'followers')
        }),
    )

    list_display = ('user', 'nome', 'email', 'descrizione')
    search_fields = ('user', 'nome', 'email', 'descrizione')

admin.site.register(Utente, UtenteAdmin)
admin.site.register(Organizzatore, OrganizzatoreAdmin)