from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from .models import Utente, Organizzatore

class UtenteInline(admin.StackedInline):
    model = Utente
    can_delete = False
    verbose_name = 'Additional information'

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
    inlines = (UtenteInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class UtenteAdmin(admin.ModelAdmin):
    model = Utente

    def get_username(self, obj):
        return obj.user.username
    
    list_display = ('get_username', 'email', 'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono')
    search_fields = ('get_username', 'email', 'nome', 'cognome', 'data_nascita', 'sesso', 'stato', 'indirizzo', 'telefono')

admin.site.register(Utente, UtenteAdmin)
admin.site.register(Organizzatore)