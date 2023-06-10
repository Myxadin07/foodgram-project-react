from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UsersViewSet, IngredientsViewSet, RecipesViewSet,
                    TagsViewSet)

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
