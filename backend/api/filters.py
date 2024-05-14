from django_filters import BooleanFilter, CharFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet

from recipe.models import Product, Tag, Recipe


class ProductFilter(FilterSet):
    '''Filter for products.'''

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Product
        fields = ['name']


class RecipeFilter(FilterSet):
    '''Filter for recipes.'''

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart')
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
