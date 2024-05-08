import base64

from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework.serializers import (
    SerializerMethodField, ValidationError, ImageField, ModelSerializer,
    PrimaryKeyRelatedField
)
from rest_framework.exceptions import NotAuthenticated

from backend.settings import USER_URL_PATH_NAME
from recipe.models import (
    Favorite, Follow, FoodgramUser, Ingredient, Product, Recipe, ShoppingCart,
    Tag
)


def make_ingredients(validated_data, recipe=False):
    '''
    Edit an existing recipe entry
    or add a new one if there is no such recipe.
    '''

    ingredients = validated_data.pop('ingredients')
    tags = validated_data.pop('tags')
    if not recipe:
        recipe = Recipe.objects.create(**validated_data)
    else:
        Ingredient.objects.filter(recipe_id=recipe.pk).delete()
    recipe.tags.set(tags)
    for ingredient_data in ingredients:
        amount = ingredient_data['amount']
        product = ingredient_data['product']
        Ingredient.objects.create(
            recipe=recipe, amount=amount, product=product
        )
    return recipe


def get_availability_object(model, kwargs):
    '''
    Returns bool, there is an entry with the specified parameters in the model
    or not.
    '''
    if not kwargs['user'].is_authenticated:
        return False
    if model.objects.filter(**kwargs).exists():
        return True
    return False


class RecipeUserSerializer(UserCreateSerializer):
    """
    A serializer for displaying users when called from another serializer.
    """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = FoodgramUser
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password', 'id',
            'is_subscribed'
        )

    def get_fields(self):
        if (
            self.context['request'].path == USER_URL_PATH_NAME
            and not self.context['request'].user.is_authenticated
        ):
            raise NotAuthenticated(
                detail='User is not authenticated')
        return super().get_fields()

    def get_is_subscribed(self, obj):
        '''
        Returns the bool value at which the user is subscribed to another user
        or not.
        '''
        return get_availability_object(model=Follow, kwargs={
            'user': self.context['request'].user, 'following': obj
        })


class FoodgramUserSerializer(RecipeUserSerializer):
    """A serializer for users."""

    def to_representation(self, instance):
        if self.context['request'].method != 'GET':
            self.fields.pop('is_subscribed')
        return super().to_representation(instance)


class Base64ImageField(ImageField):
    '''A field that converts images to base64 format and back.'''

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """A serializer for tags."""

    class Meta:
        model = Tag
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    '''Serializer for products.'''

    class Meta:
        model = Product
        fields = '__all__'


class TagPrimaryKeyRelatedField(PrimaryKeyRelatedField):
    '''A field displaying tag data via the PrimaryKeyRelatedField.'''

    def to_representation(self, value):
        return model_to_dict(value)


class IngredientSerializer(ModelSerializer):
    '''
    A serializer for displaying ingredients
    when called from another serializer.
    '''

    class Meta:
        model = Ingredient
        fields = 'product', 'amount'

    def to_internal_value(self, data):
        data['product'] = data.pop('id')
        return super().to_internal_value(data)

    def to_representation(self, instance):
        result = model_to_dict(instance.product)
        result['amount'] = instance.amount
        return result


class RecipeSerializer(ModelSerializer):
    """A serializer for recipes."""

    author = RecipeUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagPrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = IngredientSerializer(many=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        return make_ingredients(validated_data)

    def update(self, instance, validated_data):
        return make_ingredients(validated_data, recipe=instance)

    def get_is_favorited(self, obj):
        '''
        Return the bool value the user is subscribed to the recipe
        or not.
        '''
        return get_availability_object(model=Favorite, kwargs={
            'user': self.context['request'].user, 'favorite_recipe': obj
        })

    def get_is_in_shopping_cart(self, obj):
        '''
        Return the bool value there is a recipe in the shopping list
        or not.
        '''
        return get_availability_object(model=ShoppingCart, kwargs={
            'user': self.context['request'].user, 'recipe': obj
        })


class ShoppingRecipeSerializer(ModelSerializer):
    '''
    A serializer for displaying recipes when called from another serializer.
    '''

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = 'id', 'image', 'cooking_time', 'name'


class ShoppingCartSerializer(ModelSerializer):
    '''Serializer for shopping cart.'''

    recipe = ShoppingRecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = 'recipe',

    def validate(self, attrs):
        request = self.context['request']
        if request.method == 'POST':
            recipe = get_object_or_404(
                Recipe,
                pk=self.context['view'].kwargs.get('recipe_id')
            )
            if ShoppingCart.objects.filter(
                recipe=recipe, user=request.user
            ).exists():
                raise ValidationError(
                    "Вы уже добавили этот рецепт в список подупок."
                )
        return attrs

    def to_representation(self, instance):
        return super().to_representation(instance)['recipe']


class DownloadShoppingCartSerializer(ModelSerializer):
    '''
    The serializer of ingredients for later addition to the download file.
    '''

    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = 'ingredients',


class FollowingSerialiser(RecipeUserSerializer):
    """
    A serializer for displaying users when called from FollowSerializer.
    """

    recipes = ShoppingRecipeSerializer(read_only=True, many=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        model = FoodgramUser
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password', 'id',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        '''Get the count of the author's recipes.'''
        return obj.recipes.filter(author=obj).count()


class FollowSerializer(ModelSerializer):
    """Serializer for follower."""

    following = FollowingSerialiser(read_only=True)

    class Meta:
        model = Follow
        fields = 'following',

    def validate(self, attrs):
        request = self.context['request']
        if request.method == 'POST':
            following = get_object_or_404(
                FoodgramUser,
                pk=self.context['view'].kwargs.get('following_id')
            )
            user = request.user
            if Follow.objects.filter(following=following, user=user).exists():
                raise ValidationError(
                    'you have already subscribed to the '
                    f'{following.first_name} {following.last_name}.'
                )
            if following == user:
                raise ValidationError('You cant subscribe to yourself.')
        return attrs


class FavoriteSerializer(ModelSerializer):
    '''Serializer for subscribing to recipes'''

    favorite_recipe = ShoppingRecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = 'favorite_recipe',

    def validate(self, attrs):
        request = self.context['request']
        if request.method == 'POST':
            favorite_recipe = get_object_or_404(
                Recipe,
                pk=self.context['view'].kwargs.get('favorite_recipe_id')
            )
            user = request.user
            if favorite_recipe.author == user:
                raise ValidationError('You cant subscribe to your recipe.')
            if Favorite.objects.filter(
                favorite_recipe=favorite_recipe, user=user
            ).exists():
                raise ValidationError(
                    f'you have already subscribed to the '
                    f'{favorite_recipe.name}.'
                )
        return attrs

    def to_representation(self, instance):
        return super().to_representation(instance)['favorite_recipe']
