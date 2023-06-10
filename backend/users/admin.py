from django.contrib import admin

from .models import Users


class UsersAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(Users, UsersAdmin)
