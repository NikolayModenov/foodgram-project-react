from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    SerializerMethodField, ModelSerializer, PrimaryKeyRelatedField,
    IntegerField
)

from recipe.models import (
    Favorite, Follow, FoodgramUser, Ingredient, Product, Recipe, ShoppingCart,
    Tag
)


def get_availability_object(model, kwargs):
    '''
    Returns bool, there is an entry with the specified parameters in the model
    or not.
    '''
    if not kwargs['user'].is_authenticated:
        return False
    return model.objects.filter(**kwargs).exists()


class CreateUserSerializer(UserCreateSerializer):
    '''
    A serializer for displaying users when called from another serializer.
    '''

    class Meta:
        model = FoodgramUser
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password', 'id'
        )


class FoodgramUserSerializer(CreateUserSerializer):
    '''A serializer for users.'''

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta(CreateUserSerializer.Meta):
        fields = CreateUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, author):
        return get_availability_object(model=Follow, kwargs={
            'user': self.context['request'].user, 'author': author
        })


class TagSerializer(ModelSerializer):
    '''A serializer for tags.'''

    class Meta:
        model = Tag
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    '''Serializer for products.'''

    class Meta:
        model = Product
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    '''
    A serializer for displaying ingredients
    when called from another serializer.
    '''

    product = PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Ingredient
        fields = 'product', 'amount'

    def to_internal_value(self, data):
        data['product'] = data.pop('id')
        return super().to_internal_value(data)

    def to_representation(self, instance):
        result = super().to_representation(instance)
        prods = get_object_or_404(Product, pk=result.pop('product'))
        result['id'] = prods.pk
        result['name'] = prods.name
        result['measurement_unit'] = prods.measurement_unit
        return result


class RecipeSerializer(ModelSerializer):
    '''A serializer for recipes.'''

    author = FoodgramUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = IngredientSerializer(many=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        exclude = 'pub_date',

    def to_representation(self, instance):
        result = super().to_representation(instance)
        tags_id = result.pop('tags')
        tags = list()
        for tag_id in tags_id:
            res_tag = dict()
            tag = get_object_or_404(Tag, pk=tag_id)
            res_tag['id'] = tag.pk
            res_tag['name'] = tag.name
            res_tag['color'] = tag.color
            res_tag['slug'] = tag.slug
            tags.append(res_tag)
        result['tags'] = tags
        return result

    def get_is_favorited(self, obj):
        '''
        Return the bool value the user is subscribed to the recipe
        or not.
        '''
        return get_availability_object(model=Favorite, kwargs={
            'user': self.context['request'].user, 'recipe': obj
        })

    def get_is_in_shopping_cart(self, obj):
        '''
        Return the bool value there is a recipe in the shopping list
        or not.
        '''
        return get_availability_object(model=ShoppingCart, kwargs={
            'user': self.context['request'].user, 'recipe': obj
        })


class InfoRecipeSerializer(ModelSerializer):
    '''
    A serializer for displaying recipes when called from another serializer.
    '''

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = 'id', 'image', 'cooking_time', 'name'


class FollowingSerialiser(FoodgramUserSerializer):
    '''
    A serializer for displaying users when called from another serializer.
    '''

    recipes = InfoRecipeSerializer(read_only=True, many=True)
    recipes_count = IntegerField(read_only=True, source='recipes.count')

    class Meta:
        model = FoodgramUser
        fields = FoodgramUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )


class FollowSerializer(ModelSerializer):
    '''Serializer for follower.'''

    author = FollowingSerialiser(read_only=True)

    class Meta:
        model = Follow
        fields = 'author',

    def to_representation(self, instance):
        return super().to_representation(instance)['author']
