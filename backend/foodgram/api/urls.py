from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, CustomUserViewset,
                    TagsViewSet, RecipesViewSet,
                    SubscriptionsView, FollowUserView)

router = DefaultRouter()
router.register('users', CustomUserViewset, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
    path('users/<int:id>/subscribe/', FollowUserView.as_view(), name='subscribe'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
