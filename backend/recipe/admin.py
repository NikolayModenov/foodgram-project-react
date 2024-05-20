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

    def lookups(self, request, model_admin):

        chart_data = self.calculate_chart_data().values("time_slice").annotate(
            count=Count("id")
        ).order_by("time_slice")

        filter_messages = dict()
        for i in range(len(chart_data)):
            upper_threshold = chart_data[i]["time_slice"]
            count = chart_data[i]["count"]

            if i == 0:
                filter_messages[upper_threshold] = (
                    f'Быстрее {upper_threshold} минут ({count})'
                )
                continue

            lower_threshold = chart_data[i - 1]["time_slice"]

            if upper_threshold == 'inf':
                filter_messages[upper_threshold] = (
                    f'Дольше {lower_threshold} минут ({count})'
                )
                continue

            filter_messages[upper_threshold] = (
                f'От {lower_threshold} минут до {upper_threshold} минут '
                f'({count})'
            )
        return list(filter_messages.items())

    def queryset(self, request, queryset):
        if self.value():
            return self.calculate_chart_data(queryset).filter(
                time_slice=self.value()
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
        return user.recipe_favorite_user.count()

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
        return ''.join([
            f'<p>{ingredient.product.name[:10]} {ingredient.amount} '
            f'{ingredient.product.measurement_unit}</p>'
            for ingredient
            in recipe.ingredients.all()
        ])

    @mark_safe
    @admin.display(description='Тэги')
    def preview_tags(self, recipe):
        return ''.join([f'<p>{tag.name}</p>' for tag in recipe.tags.all()])


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
