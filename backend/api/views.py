from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from recipes.models import (
    Ingredients, IngredientsInRecipes, Recipes, ShoppingCart, Tags
)
from users.models import Users

from .filters import IngredientsFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserSerializer, IngredientsSerializer, TagsSerializer,
    SerializerForCreatedRecipes, ReadRecipeSerializer, CreateRecipeSerializer
)
from .pagination import NumberPerPage

User = get_user_model()


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filterset_class = IngredientsFilter
    filter_backends = [DjangoFilterBackend]


class CustomUserViewset(UserViewSet):
    queryset = Users.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = NumberPerPage
    permission_classes = [IsAuthenticated]

    @action(
        methods=('GET',),
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def show_subscriptions(self, request):
        return super().list(request)

    def get_queryset(self):
        if self.action == "show_subscriptions":
            return self.request.user.subscriptions.all()
        return super().get_queryset()

    @action(
        methods=['DELETE', 'POST'],
        detail=True,
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe_or_unsubscribe(self, request, id=None):
        user = self.get_object()
        subscriber = request.user
        if request.method == 'POST':
            subscriber.subscriptions.add(user)
            return Response(
                {'message': 'Вы успешно подписались'},
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            subscriber.subscriptions.remove(user)
            return Response(
                {'message': 'Вы успешно отписались'},
                status=status.HTTP_204_NO_CONTENT
            )


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

    def add_to(self, model, user, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        obj, created = model.objects.get_or_create(user=user)
        obj.recipes.add(recipe)
        if created or obj:
            serializer = SerializerForCreatedRecipes(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_304_NOT_MODIFIED)

    def delete_from(self, model, user, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        obj = get_object_or_404(model, user=user, recipes=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Users, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(Users, request.user, pk)

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
        shopping_cart_filter = request.user.users_shopping_cart.recipes.all()
        ingredient_filter = IngredientsInRecipes.objects.filter(
            recipe__in=shopping_cart_filter
        )
        ingredients = {}
        for ingredient in ingredient_filter:
            if ingredient.ingredient in ingredients.keys():
                ingredients[ingredient.ingredient] += ingredient.amount
            else:
                ingredients[ingredient.ingredient] = ingredient.amount

        shopping_list = []
        for k, v in ingredients.items():
            shopping_list.append(f'{k} - {v} {k} \n')

        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
