from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, CustomUserViewset,
                    TagsViewSet, RecipesViewSet,
                    )

router = DefaultRouter()
router.register('users', CustomUserViewset, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]


# class RecipesViewSet(viewsets.ModelViewSet):
#     queryset = Recipes.objects.all()
#     serializer_class = CreateRecipeSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = RecipeFilter
#     permission_classes = (AllowAny,)

#     def get_serializer_class(self):
#         if self.request.method in ('POST', 'PATCH'):
#             return CreateRecipeSerializer
#         return ReadRecipeSerializer

#     def add_to(self, model, user, pk):
#         user = self.request.user.id
#         recipe = get_object_or_404(Recipes, pk=pk)
#         obj, created = model.objects.get_or_create(user_id=user)
#         obj.recipes.add(recipe)
#         if created or obj:
#             serializer = SerializerForCreatedRecipes(recipe)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(status=status.HTTP_304_NOT_MODIFIED)

#     def delete_from(self, model, user, pk):
#         recipe = get_object_or_404(Recipes, pk=pk)
#         obj = get_object_or_404(model, user_id=user, recipes=recipe)
#         obj.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(
#         detail=True,
#         methods=('POST', 'DELETE'),
#         url_path='favorite',
#         permission_classes=[IsAuthenticated]
#     )
#     def favorite(self, request, pk):
#         if request.method == 'POST':
#             return self.add_to(Users, request.user, pk)
#         elif request.method == 'DELETE':
#             return self.delete_from(Users, request.user, pk)

#     @action(
#         detail=True,
#         methods=('POST', 'DELETE'),
#         url_path='shopping_cart',
#         permission_classes=[IsAuthenticated]
#     )
#     def shopping_cart(self, request, pk):
#         if request.method == 'POST':
#             return self.add_to(ShoppingCart, request.user, pk)
#         elif request.method == 'DELETE':
#             return self.delete_from(ShoppingCart, request.user, pk)

#     @action(
#         detail=False,
#         permission_classes=[IsAuthenticated],
#         methods=['get']
#     )
#     def download_shopping_cart(self, request):
#         """"Вывод списка покупок в текстовый файл"""
#         shopping_cart_filter = request.user.shopping_cart.recipes.all()
#         ingredient_filter = IngredientsInRecipes.objects.filter(
#             recipe__in=shopping_cart_filter
#         ).values('ingredient__name').annotate(total_amount=Sum('amount'))
#         shopping_list = [(f"{item['ingredient__name']}"
#                           f" - {item['total_amount']}"
#                           f" \n") for item in ingredient_filter]
#         response = HttpResponse(shopping_list, 'Content-Type: text/plain')
#         response['Content-Disposition'] = (
#             'attachment; filename="shopping_list.txt"'
#         )
#         return response
