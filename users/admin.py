from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Organizzatore, Utente

class UtenteAdmin(UserAdmin):
    model = Utente

    # i campi first_name e last_name vengono aggiornati rispettivamente sulla base di nome e cognome
    readonly_fields = ('first_name', 'last_name')

    # campi visualizzati nel modulo di modifica dell'utente nel pannello di amministrazione
    fieldsets = (
        ('Personal info', {
            'fields': ('nome', 'cognome', 'username', 'email', 'password', 'is_active', 'is_staff')
        }),
        ('Additional Information', {
            'fields': ('first_name', 'last_name', 'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono', 'carta_credito', 'cvv', 'scadenza_carta', 'notifiche')
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions', 'is_superuser')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # campi visualizzati nel modulo di aggiunta dell'utente nel pannello di amministrazione
    add_fieldsets = (
        ('Personal info', {
            'fields': ('nome', 'cognome', 'username', 'email', 'password1', 'password2')
        }),
        ('Additional Information', {
            'fields': ('data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono', 'carta_credito', 'cvv', 'scadenza_carta', 'notifiche')
        }),
    )

    # campi visualizzati nella lista degli utenti
    list_display = ('username', 'email', 'nome', 'cognome', 'is_staff', 'is_active')

    # campi con i quali è possibili ricercare gli utenti
    search_fields = ('username', 'email', 'nome', 'cognome')

admin.site.register(Utente, UtenteAdmin)
admin.site.register(Organizzatore)