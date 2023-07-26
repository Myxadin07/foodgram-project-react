from django_filters import rest_framework as filters

from recipes.models import (Ingredients, Recipes)


class IngredientsFilter(filters.FilterSet):
    name = filters. CharFilter(lookup_expr='istartswith')
    # search_param = 'name'
    # name = filters.CharFilter(
    #     search_param='name',
    #     lookup_expr='istartswith'
    # )

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author__id')
    filter_is_favorited = filters.BooleanFilter(method='is_favorited')
    filter_is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = ('tags', 'author')

    def is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                recipe_shopping_cart__user=self.request.user)
        return queryset

        
# для комита
