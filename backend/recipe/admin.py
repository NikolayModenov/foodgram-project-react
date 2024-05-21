from collections import defaultdict


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count, Value, Case, When, CharField
from django.utils.safestring import mark_safe

from recipe.models import (
    FoodgramUser, Follow, Ingredient, Tag, Recipe, Favorite, Product,
    ShoppingCart
)

BOUNDARY_VALUES = (15, 45)


class RecipesOrFollowersFilter(admin.SimpleListFilter):

    title = 'Подписки'
    parameter_name = 'Подписка'

    def lookups(self, request, model_admin):
        return [
            ('favorite_recipes', 'рецепты'),
            ('followers', 'авторы'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'favorite_recipes':
            return queryset.filter(favorites__isnull=False)
        if self.value() == 'followers':
            return queryset.filter(authors__isnull=False)


class CookingTimeFilter(admin.SimpleListFilter):

    title = 'Время приготовления'
    parameter_name = 'Время приготовления'

    @staticmethod
    def calculate_chart_data(queryset=Recipe.objects):

        slice_pattern = [
            When(cooking_time__lte=val, then=Value(str(val)))
            for val in BOUNDARY_VALUES
        ]

        return queryset.annotate(time_slice=Case(
            *slice_pattern,
            default=Value('inf'),
            output_field=CharField(),
        ))
    
    @staticmethod
    def get_bin(time):
        for el in BOUNDARY_VALUES:
            if el >= time:
                return str(el)
        return 'inf'

    @staticmethod
    def format_time_message(left, rigth, count):
        if left == '0':
            return f'Быстрее {rigth} минут ({count})'
        if rigth == 'inf':
            return f'Дольше {left} минут ({count})'
        return f'От {left} минут до {rigth} минут ({count})'

    def lookups(self, request, model_admin):
        chart_data = defaultdict(int)
        for recipe in Recipe.objects.all():
            bin = self.get_bin(recipe.cooking_time)
            chart_data[bin] += 1

        filter_messages = dict()
        left_time = '0'
        values = sorted([str(value) for value in BOUNDARY_VALUES])
        values.append('inf')
        for right_time in values:
            filter_messages[right_time] = self.format_time_message(
                left_time, right_time, chart_data[right_time]
            )
            left_time = right_time

        return list(filter_messages.items())

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'inf':
                return queryset.filter(cooking_time__gt=BOUNDARY_VALUES[-1])
            if int(self.value()) == BOUNDARY_VALUES[0]:
                return queryset.filter(cooking_time__lte=int(self.value()))

            left_time = BOUNDARY_VALUES[
                BOUNDARY_VALUES.index(int(self.value())) - 1
            ]
            return queryset.filter(
                cooking_time__gt=left_time,
                cooking_time__lte=int(self.value())
            )
        return queryset


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'recipes_count',
        'favorite_recipes_count', 'followers_count'
    )
    list_filter = (RecipesOrFollowersFilter,)
    search_fields = ('username', 'first_name', 'last_name')

    @admin.display(description='Рецепты')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписчиков')
    def favorite_recipes_count(self, user):
        return user.favorites.count()

    @admin.display(description='Подписок')
    def followers_count(self, user):
        return user.authors.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass
    list_display = ('user', 'author')


@admin.register(Ingredient)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    list_filter = ('measurement_unit',)
    search_fields = ('name', 'measurement_unit')

    @admin.display(description='Рецепты')
    def recipes_count(self, product):
        return Recipe.objects.filter(ingredients__product=product).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview_color', 'color', 'slug')

    @mark_safe
    @admin.display(description='Цвет')
    def preview_color(self, tag):
        return (
            f'<div style="background-color: {tag.color};width: 50%;height: '
            f'20px;text-align: center; padding-top: 4px;"></div>'
        )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'cooking_time', 'preview_image',
        'preview_ingredients', 'preview_tags'
    )
    list_filter = ('tags', CookingTimeFilter)
    search_fields = ('name', 'tags__name')

    @mark_safe
    @admin.display(description='Изображение')
    def preview_image(self, recipe):
        return f'<img src="{recipe.image}" width=50>'

    @mark_safe
    @admin.display(description='Ингредиенты')
    def preview_ingredients(self, recipe):
        return '<br>'.join(
            f'{ingredient.product.name[:20]} {ingredient.amount} '
            f'{ingredient.product.measurement_unit}'
            for ingredient
            in recipe.ingredients.all()
        )

    @mark_safe
    @admin.display(description='Тэги')
    def preview_tags(self, recipe):
        return '<br>'.join(f'{tag.name}' for tag in recipe.tags.all())


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Product)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'product', 'amount')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.unregister(Group)
