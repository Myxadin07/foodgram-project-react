from django_filters import rest_framework as filters

from recipes.models import (
    Favorite_Recipes, Ingredients, Recipes, Shoppingcart, Tags
)


class IngredientsFilter(filters.FilterSet):

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipesFilter(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        queryset=Tags.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_subscribed = filters.BooleanFilter(
        method='filter_is_subscribed'
    )

    class Meta:
        model = Recipes
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user

        if Favorite_Recipes.objects.filter(user=user).exists():
            return queryset.filter(favorite_recipe__user=user)

        return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user

        if Shoppingcart.objects.filter(user=user).exists():
            return queryset.filter(shoppingcart_recipe__user=user)

        return queryset.none()

    def filter_is_subscribed(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(author=user)
