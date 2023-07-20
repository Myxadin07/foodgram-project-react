from django.contrib import admin

from .models import Users


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email',)
    search_fields = (
        'id', 'username', 'password',
        'email', 'first_name', 'last_name'
    )
    empty_value_display = '-пусто-'
