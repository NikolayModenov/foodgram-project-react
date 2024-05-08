from django.urls import include, path
from rest_framework.routers import DefaultRouter, Route

from api.views import (
    FavoriteViewSet, FollowViewSet, ProductViewSet, RecipeViewSet,
    ShoppingCartViewSet, TagViewSet
)


class ShoppingCartRouter(DefaultRouter):
    routes = [
        Route(
            url=r'recipes/(?P<recipe_id>\d+)/shopping_cart',
            mapping={
                'post': 'create',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=False,
            initkwargs={'suffix': 'Instance'}
        ),
    ]


class FavoriteRouter(DefaultRouter):
    routes = [
        Route(
            url=r'recipes/(?P<favorite_recipe_id>\d+)/favorite',
            mapping={
                'post': 'create',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=False,
            initkwargs={'suffix': 'Instance'}
        ),
    ]


class FollowRouter(DefaultRouter):
    routes = [
        Route(
            url=r'users/subscribe',
            mapping={
                'get': 'list'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'users/(?P<following_id>\d+)/subscribe',
            mapping={
                'post': 'create',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=False,
            initkwargs={'suffix': 'Instance'}
        ),
    ]


router_v1 = DefaultRouter()

shopping_cart_router = ShoppingCartRouter()
follow_router = FollowRouter()
favorite_router = FavoriteRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', ProductViewSet, basename='ingredients')
shopping_cart_router.register('', ShoppingCartViewSet, basename='shopping_cart')
follow_router.register('', FollowViewSet, basename='subscribe')
favorite_router.register('', FavoriteViewSet, basename='subscribe')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include(shopping_cart_router.urls)),
    path('', include(follow_router.urls)),
    path('', include(favorite_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
