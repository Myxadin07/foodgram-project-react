from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite_Recipes, IngredientInRecipe, Ingredients,
                            Recipes, Shoppingcart, Subscriptions, Tags)

from .filters import IngredientsFilter, RecipesFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (UserSerializer, IngredientsSerializer,
                          RecipeMinifiedSerializer, AddRecipesSerializer,
                          RecipesSerializer, SubscriptionsSerializer,
                          TagsSerializer)
from .utils import add_or_delete_recipes_view

User = get_user_model()


class UsersViewSet(UserViewSet):
    '''Вьюсет для обработки всех запросов от пользователей'''
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        '''Подписаться на пользователя'''
        user = request.user
        author_id = kwargs['id']
        author_obj = get_object_or_404(User, id=author_id)

        serializer = SubscriptionsSerializer(
            instance=author_obj,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            Subscriptions.objects.create(
                user=user, author_id=author_id
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        '''Метод отписки от пользователя'''
        user = request.user
        author_id = kwargs['id']

        if get_object_or_404(
            Subscriptions,
            user=user,
            author_id=author_id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        '''
        Возращает подписки пользователя и добавляет рецепты
        '''
        subscriptions = User.objects.filter(
            following__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filterset_class = IngredientsFilter
    permission_classes = (IsAdminOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)

    def get_serializer_class(self):
        """
        Возвращает сериализатор соответствующий запросу:
        GET, DELETE - RecipesSerializer;
        POST, UPDATE, DELETE - RecipesAddSerializer.
        """
        if self.action in ('create', 'partial_update'):
            return AddRecipesSerializer
        return RecipesSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, **kwargs):
        '''Метод добавляет или удаляет рецепт в/из корзину(ы)'''
        return add_or_delete_recipes_view(
            request, Shoppingcart, RecipeMinifiedSerializer, **kwargs
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, **kwargs):
        '''Добавляет или удаляет рецепт в избранные пользователю'''
        return add_or_delete_recipes_view(
            request, Favorite_Recipes, RecipeMinifiedSerializer, **kwargs
        )

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request):
        '''Скачать список покупок одним файлом (формат txt)'''
        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__shoppingcart_recipe__user=request.user,
        ).order_by('ingredient__name').values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = f'Список покупок {request.user}:\n'
        for iter, (name, unit, amount) in enumerate(shopping_cart, start=1):
            shopping_list += f'\n {iter}. {name} ({unit}) - {amount}'

        filename = 'data.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
