from django.contrib import admin
from django.contrib.admin import display

from .models import (Favorite_Recipes, IngredientInRecipe, Ingredients,
                     Recipes, Shoppingcart, Subscriptions, Tags)


class IngrediensInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    fields = ('ingredient', 'amount',)


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorite',)
    search_fields = ('author', 'name', 'tags',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (IngrediensInRecipeInline,)
    empty_value_display = '-пусто-'

    @display(description='Количество в избранных')
    def count_favorite(self, kwags):
        return kwags.favorite_recipe.count()


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tags)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(Favorite_Recipes)
admin.site.register(Shoppingcart)
admin.site.register(Subscriptions)
