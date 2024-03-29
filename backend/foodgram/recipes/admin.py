from django.contrib import admin

from .models import (Ingredients, Tags, Recipes, IngredientsInRecipes)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientsInRecipes
    readonly_fields = ('measurement_unit',)

    def measurement_unit(self, instance):
        return instance.ingredient.measurement_unit


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('author', 'name', 'tags',)
    list_filter = ('author', 'name', 'tags',)
    readonly_fields = ('count_add_to_favorite',)
    empty_value_display = '-пусто-'
    inlines = (IngredientInRecipeInline,)

    def count_add_to_favorite(self, instance):
        return instance.favorites.count()


admin.site.register(Tags)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
