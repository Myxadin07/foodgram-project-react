from django_filters import rest_framework as filters
from distutils.util import strtobool

from recipes.models import (Ingredients, Recipes, Tags, Favorite, ShoppingCart)

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True')
)


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name="slug",
    )
    is_favorited = filters.BooleanFilter(method='get_filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset
    # tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    # author = filters.NumberFilter(field_name='author__id')
    # filter_is_favorited = filters.BooleanFilter(method='is_favorited')
    # filter_is_in_shopping_cart = filters.BooleanFilter(
    #     method='is_in_shopping_cart')

    # class Meta:
    #     model = Recipes
    #     fields = ('tags', 'author')

    # def is_favorited(self, queryset, name, value):
    #     if value:
    #         return queryset.filter(favorite__user=self.request.user)
    #     return queryset

    # def is_in_shopping_cart(self, queryset, name, value):
    #     if value:
    #         return queryset.filter(
    #             recipe_shopping_cart__user=self.request.user)
    #     return queryset
