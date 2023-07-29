from django_filters import rest_framework as filters

from recipes.models import (Ingredients, Recipes, Tags)

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
