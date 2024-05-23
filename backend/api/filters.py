from django.forms.widgets import NullBooleanSelect
from django_filters import BooleanFilter, CharFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet

from recipe.models import Ingredient, Tag, Recipe


class ProductFilter(FilterSet):
    '''Filter for products.'''

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class BoolOrIntSelect(NullBooleanSelect):

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        return {
            True: True,
            'True': True,
            'False': False,
            False: False,
            'true': True,
            'false': False,
            '1': True,
            '0': False,
        }.get(value)


class RecipeFilter(FilterSet):
    '''Filter for recipes.'''

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')
    is_favorited = BooleanFilter(
        method='get_is_favorited', widget=BoolOrIntSelect
    )
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart', widget=BoolOrIntSelect
    )
    author = CharFilter(field_name='author_id')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def base_filtration(self, queryset, value, kwargs):
        '''
        Returns bool,
        there is an entry with the specified parameters in the model
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
