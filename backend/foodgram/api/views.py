from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, exceptions, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from recipes.models import (
    Ingredients, IngredientsInRecipes, Recipes, ShoppingCart, Tags, Favorite
)
from users.models import Users, Follow
from .filters import IngredientsFilter, RecipeFilter
from .serializers import (
    IngredientsSerializer, TagsSerializer,
    SerializerForCreatedRecipes, ReadRecipeSerializer, CreateRecipeSerializer,
    SubscriptionSerializer
)
from .pagination import NumberPerPage

User = get_user_model()


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filterset_class = IngredientsFilter


class CustomUserViewset(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = NumberPerPage

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.follower.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = Users.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Подписка на самого себя запрещена.'
                )
            if Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError('Подписка уже оформлена.')

            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Подписка не была оформлена, либо уже удалена.'
                )

            subscription = get_object_or_404(
                Follow,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = CreateRecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def add_to(self, model, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        if model.objects.filter(user=user, recipes_id=recipe
                                ).exists():
            raise exceptions.ValidationError('Рецепт уже в избранном.')
        model.objects.create(user=user, recipes=recipe)
        serializer = SerializerForCreatedRecipes(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        if not model.objects.filter(user=user, recipe_id=recipe
                                    ).exists():
            raise exceptions.ValidationError(
                'Рецепта нет в избранном, либо он уже удален.'
            )
        favorite = get_object_or_404(model, user=user, recipes=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request, pk)
        elif request.method == 'DELETE':
            return self.delete_from(Favorite, request.user.id, pk)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['get']
    )
    def download_shopping_cart(self, request):
        """"Вывод списка покупок в текстовый файл"""
        shopping_cart_filter = request.user.shopping_cart.recipes.all()
        ingredient_filter = IngredientsInRecipes.objects.filter(
            recipe__in=shopping_cart_filter
        ).values('ingredient__name').annotate(total_amount=Sum('amount'))
        shopping_list = [(f"{item['ingredient__name']}"
                          f" - {item['total_amount']}"
                          f" \n") for item in ingredient_filter]
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
