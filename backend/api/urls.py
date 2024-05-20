from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    ProductViewSet, RecipeViewSet, TagViewSet, FoodgramUserViewSet
)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', ProductViewSet, basename='ingredients')
router.register('users', FoodgramUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
