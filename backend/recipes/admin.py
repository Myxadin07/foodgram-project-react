from django.contrib import admin

from .models import (Ingredients, Tags)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tags)
admin.site.register(Ingredients, IngredientsAdmin)
