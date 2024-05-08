from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import BooleanFilter, CharFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.viewsets import (ModelViewSet, ReadOnlyModelViewSet)

from api.permissions import IsAuthor, RecipePermissions
from api.serializers import (
    DownloadShoppingCartSerializer, FavoriteSerializer, FollowSerializer,
    ProductSerializer, RecipeSerializer, ShoppingCartSerializer, TagSerializer
)
from backend.settings import DOWNLOAD_URL_PATH_NAME
from recipe.models import (
    FoodgramUser, Product, Recipe, ShoppingCart, Tag
)


class ProductFilter(FilterSet):
    '''Filter for products.'''

    name = CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Product
        fields = ["name"]


class RecipeFilter(FilterSet):
    '''Filter for recipes.'''

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug")
    is_favorited = BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = BooleanFilter(
        method="get_is_in_shopping_cart")
    author = CharFilter(field_name="author_id")

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def base_filtration(self, queryset, value, kwargs):
        '''
        Returns bool, there is an entry with the specified parameters in the model
        or not.
        '''
        if value and self.request.user.is_authenticated:
            return queryset.filter(**kwargs)
        return queryset

    def get_is_favorited(self, queryset, key, value):
        '''
        Return the bool value the user is subscribed to the recipe
        or not.
        '''
        return self.base_filtration(
            queryset, value, kwargs={'favorite__user': self.request.user}
        )

    def get_is_in_shopping_cart(self, queryset, key, value):
        '''
        Return the bool value there is a recipe in the shopping list
        or not.
        '''
        return self.base_filtration(
            queryset, value, kwargs={'shopping_cart__user': self.request.user}
        )


class TagViewSet(ReadOnlyModelViewSet):
    """A viewset for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class ProductViewSet(ReadOnlyModelViewSet):
    """Viewset for products."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """A viewset for recipes."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (RecipePermissions,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['GET'],
        detail=False,
        url_path=DOWNLOAD_URL_PATH_NAME
    )
    def get_shopping_cart(self, request):
        '''Download the list of ingredients to buy.'''
        recipes = ShoppingCart.objects.filter(user=1)
        rec = list()
        for recipe in recipes:
            r = recipe.recipe
            rec.append(r)
        serializer = DownloadShoppingCartSerializer(rec, many=True)
        shopping_cart = dict()
        for ingredients in serializer.data:
            for ingredient in ingredients['ingredients']:
                key = ingredient.pop('id')
                if key in shopping_cart:
                    shopping_cart[key]['amount'] += ingredient['amount']
                else:
                    shopping_cart[key] = ingredient
        for_download = str()
        for id in shopping_cart:
            product = shopping_cart[id]
            name = product['name']
            amount = product['amount']
            measurement_unit = product['measurement_unit']
            for_download += (f'{name} = {amount} {measurement_unit}.\n')
        return HttpResponse(
            for_download, content_type='text/plain; charset=UTF-8'
        )


class ShoppingCartViewSet(ModelViewSet):
    """A viewset for shopping cart."""

    lookup_field = 'recipe_id'
    permission_classes = (IsAuthor,)
    serializer_class = ShoppingCartSerializer

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    def get_queryset(self):
        return self.get_recipe().shopping_cart.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(recipe=self.get_recipe(), user=self.request.user)


class FollowViewSet(ModelViewSet):
    """A viewset for follower."""

    serializer_class = FollowSerializer
    lookup_field = 'following_id'
    permission_classes = (IsAuthor,)
    pagination_class = None

    def get_follower(self):
        return get_object_or_404(
            FoodgramUser, pk=self.kwargs.get('following_id')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, following=self.get_follower())

    def get_queryset(self):
        return self.request.user.follower


class FavoriteViewSet(ModelViewSet):
    """A viewset for subscribing to recipes."""

    serializer_class = FavoriteSerializer
    lookup_field = 'favorite_recipe_id'
    permission_classes = (IsAuthenticated,)

    def get_favorite(self):
        return get_object_or_404(
            Recipe, pk=self.kwargs.get('favorite_recipe_id')
        )

    def get_queryset(self):
        return self.get_favorite().favorite.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user, favorite_recipe=self.get_favorite()
        )
