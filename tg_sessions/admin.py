from django.contrib import admin

from .models import TgSession


@admin.register(TgSession)
class TgSessionAdmin(admin.ModelAdmin):
    """ Админ-панель для телеграм сессий """

    save_as = True
    list_display = ['tg_session_string', 'user', 'is_active']
    list_display_links = ['user']
    list_filter = ['is_active']
    search_fields = ['user']
    fieldsets = (
        ('Основная информация', {'fields': ('user', 'tg_session_string')}),
        ('Дополнительная информация', {'fields': (
            'is_active',
        )}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )
