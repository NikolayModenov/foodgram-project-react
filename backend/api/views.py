from django.db.models import Sum, F
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import ProductFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.report_generator import format_shopping_cart_report
from api.serializers import (
    FollowSerializer, ProductSerializer, RecipeSerializer, TagSerializer,
    InfoRecipeSerializer, FollowingSerializer
)
from backend.settings import (
    DOWNLOAD_URL_PATH_NAME, SHOPPING_CART_URL_PATH_NAME,
    FAVORITE_URL_PATH_NAME, SUBSCRIBE_URL_PATH_NAME, USER_URL_PATH_NAME,
    GET_SUBSCRIPTIONS_URL_PATH_NAME
)
from recipe.models import (
    FoodgramUser, Ingredient, Recipe, ShoppingCart, Tag, Favorite, Follow,
    Product
)


SHOPPING_CART_ERROR_MESSAGE = {
    'post': 'Вы уже добавили рецепт {name} в список покупок.',
    'delete': 'У вас нет рецепта {name} в списке покупок.'
}
FAVORITE_ERROR_MESSAGE = {
    'post': 'Вы уже подписаны на рецепт {name}.',
    'delete': 'Вы не подписаны на рецепт {name}.'
}
SUBSCRIPTION_ERROR_MESSAGE = {
    'auth': 'Вы не можете подписаться на самого себя.',
    'post': 'Вы уже подписаны на автора {last_name} {first_name}.',
}


class FoodgramUserViewSet(UserViewSet):
    '''A viewset for users.'''

    def get_permissions(self):
        if self.action == USER_URL_PATH_NAME and self.request.method == 'GET':
            self.permission_classes = IsAuthenticated,
        return super().get_permissions()

    @action(
        methods=['GET'],
        detail=False,
        url_path=GET_SUBSCRIPTIONS_URL_PATH_NAME,
        permission_classes=[IsAuthenticated, ],
        serializer_class=FollowSerializer,
    )
    def get_subscriptions(self, request):
        queryset = self.request.user.users.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path=SUBSCRIBE_URL_PATH_NAME,
        permission_classes=[IsAuthenticated, ]
    )
    def change_subscription_to_author(self, request, **kwargs):
        if str(request.user.pk) == kwargs['id']:
            raise ValidationError(
                SUBSCRIPTION_ERROR_MESSAGE['auth']
            )
        author = get_object_or_404(FoodgramUser, pk=kwargs['id'])
        if self.request.method == 'POST':
            follower, created = Follow.objects.get_or_create(
                author=author, user=request.user
            )
            if not created:
                raise ValidationError(
                    SUBSCRIPTION_ERROR_MESSAGE['post'].format(
                        last_name=author.last_name,
                        first_name=author.first_name
                    )
                )
            return Response(
                FollowingSerializer(author, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(Follow, author=author, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    '''A viewset for tags.'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class ProductViewSet(ReadOnlyModelViewSet):
    '''Viewset for products.'''

    queryset = Ingredient.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    '''A viewset for recipes.'''

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def make_ingredients(self, serializer, recipe=None):
        print(serializer.validated_data)

        ingredients_data = serializer.validated_data.pop('products')
        if recipe:
            Product.objects.filter(recipe_id=recipe.pk).delete()
        recipe = serializer.save(
            author=self.request.user, **serializer.validated_data
        )
        Product.objects.bulk_create(
            Product(
                recipe=recipe, amount=ingredient_data['amount'],
                ingredient=ingredient_data['ingredient']
            )
            for ingredient_data in ingredients_data
        )

    def perform_create(self, serializer):
        self.make_ingredients(serializer=serializer)

    def perform_update(self, serializer):
        self.make_ingredients(serializer=serializer, recipe=self.get_object())

    @action(
        methods=['GET'],
        detail=False,
        url_path=DOWNLOAD_URL_PATH_NAME
    )
    def get_shopping_cart(self, request):
        '''Download the list of ingredients to buy.'''

        if not ShoppingCart.objects.filter(user=request.user.pk).exists():
            return redirect('recipes-list')
        shopping_cart = FoodgramUser.objects.get(
            pk=request.user.pk
        ).recipe_shoppingcart_user.values(
            'recipe__ingredients__product_id',
            unit=F('recipe__ingredients__product__measurement_unit'),
            name=F('recipe__ingredients__product__name'),
        ).annotate(amount=Sum('recipe__ingredients__amount'),)
        return FileResponse(format_shopping_cart_report(shopping_cart))

    def change_recipe_related_entries(self, pk, table, err_message):
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            obj, created = table.objects.get_or_create(
                recipe=recipe, user=self.request.user
            )
            if not created:
                raise ValidationError(
                    err_message['post'].format(name=recipe.name)
                )
            return Response(
                InfoRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(
            table, recipe=recipe, user=self.request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path=SHOPPING_CART_URL_PATH_NAME
    )
    def change_recipe_in_shopping_cart(self, request, pk):
        return self.change_recipe_related_entries(
            pk=pk,
            table=ShoppingCart,
            err_message=SHOPPING_CART_ERROR_MESSAGE
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path=FAVORITE_URL_PATH_NAME
    )
    def change_favorite_recipe(self, request, pk):
        return self.change_recipe_related_entries(
            pk=pk,
            table=Favorite,
            err_message=FAVORITE_ERROR_MESSAGE
        )
