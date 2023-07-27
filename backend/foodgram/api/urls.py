from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewset, IngredientsViewSet,
                    TagsViewSet, RecipesViewSet,
                    SubscriptionsList, SubscribeView)

router = DefaultRouter()
router.register('users', CustomUserViewset, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path(r'users/subscriptions/', SubscriptionsList.as_view({'get': 'list'})),
    path(r'users/<int:user_id>/subscribe/', SubscribeView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
