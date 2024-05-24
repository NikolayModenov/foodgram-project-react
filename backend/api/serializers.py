from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    SerializerMethodField, ModelSerializer, PrimaryKeyRelatedField,
    IntegerField
)

from recipe.models import (
    Favorite, Follow, FoodgramUser, Product, Ingredient, Recipe, ShoppingCart,
    Tag
)


def get_object_availability(model, **kwargs):
    '''
    Returns bool, there is an entry with the specified parameters in the model
    or not.
    '''
    return (
        kwargs['user'].is_authenticated
        and model.objects.filter(**kwargs).exists()
    )


class FoodgramUserSerializer(UserSerializer):
    '''A serializer for users.'''

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, 'is_subscribed',)

    def get_is_subscribed(self, author):
        return get_object_availability(
            model=Follow, user=self.context['request'].user, author=author
        )


class TagSerializer(ModelSerializer):
    '''A serializer for tags.'''

    class Meta:
        model = Tag
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    '''Serializer for products.'''

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    '''
    A serializer for displaying ingredients
    when called from another serializer.
    '''

    ingredient = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = Product
        fields = 'ingredient', 'amount'

    def to_internal_value(self, data):
        data['ingredient'] = data.pop('id')
        return super().to_internal_value(data)

    def to_representation(self, instance):
        result = super().to_representation(instance)
        del result['ingredient']
        return {
            **result,
            **ProductSerializer().to_representation(instance.ingredient)
        }


class RecipeSerializer(ModelSerializer):
    '''A serializer for recipes.'''

    author = FoodgramUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), allow_empty=False
    )
    ingredients = IngredientSerializer(
        many=True, source='products', allow_empty=False
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        exclude = 'pub_date',

    def to_representation(self, instance):
        result = super().to_representation(instance)
        tags_id = result.pop('tags')
        result['tags'] = [
            TagSerializer().to_representation(
                get_object_or_404(Tag, pk=tag_id)
            ) for tag_id in tags_id
        ]
        return result

    def get_is_favorited(self, obj):
        '''
        Return the bool value the user is subscribed to the recipe
        or not.
        '''
        return get_object_availability(
            model=Favorite, user=self.context['request'].user, recipe=obj
        )

    def get_is_in_shopping_cart(self, obj):
        '''
        Return the bool value there is a recipe in the shopping list
        or not.
        '''
        return get_object_availability(
            model=ShoppingCart, user=self.context['request'].user, recipe=obj
        )


class InfoRecipeSerializer(ModelSerializer):
    '''
    A serializer for displaying recipes when called from another serializer.
    '''

    class Meta:
        model = Recipe
        fields = 'id', 'image', 'cooking_time', 'name'


class FollowingSerializer(FoodgramUserSerializer):
    '''
    A serializer for displaying users when called from another serializer.
    '''

    recipes = InfoRecipeSerializer(read_only=True, many=True)
    recipes_count = IntegerField(read_only=True, source='recipes.count')

    class Meta:
        model = FoodgramUser
        fields = (
            *FoodgramUserSerializer.Meta.fields, 'recipes', 'recipes_count',
        )

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['recipes'] = result['recipes'][:3]
        return result


class FollowSerializer(ModelSerializer):
    '''Serializer for follower.'''

    author = FollowingSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = 'author',

    def to_representation(self, instance):
        return super().to_representation(instance)['author']
