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
    is_favorited = filters.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_favorited_method'
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_in_shopping_cart_method'
    )
    author = filters.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all()
    )

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipes.objects.none()

        favorites = Favorite.objects.filter(user=self.request.user)
        recipes = [item.recipes.id for item in favorites]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipes.objects.none()

        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipes.id for item in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    class Meta:
        model = Recipes
        fields = ('author', 'tags')
