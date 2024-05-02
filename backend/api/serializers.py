import base64
import six
import logging
from collections import OrderedDict
from django.forms.models import model_to_dict
from collections.abc import Mapping
from rest_framework.validators import ValidationError
from rest_framework.settings import api_settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.fields import get_error_detail, set_value, SkipField
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist


from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField, PKOnlyObject
from djoser.serializers import UserCreateSerializer

import webcolors
from django.core.files.base import ContentFile
from recipe.models import Tag, FoodgramUser, Recipe, Product, Ingredient


class FoodgramUserSerializer(UserCreateSerializer):

    class Meta:
        model = FoodgramUser
        fields = 'email', 'username', 'first_name', 'last_name', 'password', 'id'


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        model = Tag
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        model = Product
        fields = '__all__'


class TagPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return model_to_dict(value)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        model = Ingredient
        fields = 'id', 'product', 'amount'

    def to_internal_value(self, data):
        data['product'] = data.pop('id')
        return super().to_internal_value(data)

    def to_representation(self, instance):
        result = model_to_dict(instance.product)
        result['amount'] = instance.amount
        return result


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор категории."""
    author = SlugRelatedField(slug_field='username', read_only=True)
    image = Base64ImageField(required=False)
    tags = TagPrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            product = ingredient_data['product']
            Ingredient.objects.create(recipe=recipe, amount=amount, product=product)
        return recipe

    # def update(self, instance, validated_data):
    #     tags = validated_data.pop('tags')
    #     ingredients_data = validated_data.pop('ingredients')
    #     instance.tags.set(tags)
    #     ingredients = list()
    #     for ingredient_data in ingredients_data:
    #         amount = ingredient_data['amount']
    #         ingredient = get_object_or_404(Ingredient, pk=ingredient_data['id'])
    #         print(f'ingredient iter = {ingredient}')
    #         recipe_item, status = RecipeIngredient.objects.get_or_create(ingredient=ingredient, amount=amount)
    #         print(f'recipe item iter = {recipe_item}')
    #         print(f'type recipe item iter = {type(recipe_item)}')
    #         ingredients.append(recipe_item)
    #     print(f'ingredients = {ingredients}')
    #     instance.ingredients.set(ingredients)
    #     return instance
