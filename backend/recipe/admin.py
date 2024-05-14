from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipe.models import (
    FoodgramUser, Follow, Product, Tag, Recipe, Favorite, Ingredient,
    ShoppingCart
)


class RecipesOrFollowersFilter(admin.SimpleListFilter):

    title = 'Подписки'
    parameter_name = 'Подписка'

    def lookups(self, request, model_admin):
        return [
            ('favorites', 'рецепты'),
            ('followers', 'авторы'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'favorites':
            return queryset.filter(favorites__isnull=False)
        if self.value() == 'followers':
            return queryset.filter(authors__isnull=False)


class CookingTimeFilter(admin.SimpleListFilter):

    title = 'Время приготовления'
    parameter_name = 'Время приготовления'

    def lookups(self, request, model_admin):
        quickly = Recipe.objects.filter(cooking_time__lt=15).count()
        medium = Recipe.objects.filter(
            cooking_time__gte=15, cooking_time__lte=45
        ).count()
        long = Recipe.objects.filter(cooking_time__gt=45).count()
        return [
            ('quickly', f'Быстрее 15 минут ({quickly})'),
            ('medium', f'От 15 минут до 45 минут ({medium})'),
            ('long', f'долго ({long})'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'quickly':
            return queryset.filter(cooking_time__lt=15)
        if self.value() == 'medium':
            return queryset.filter(cooking_time__gte=15, cooking_time__lte=45)
        if self.value() == 'long':
            return queryset.filter(cooking_time__gt=45)


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'recipes_count',
        'favorites_count', 'followers_count'
    )
    list_filter = ('first_name', RecipesOrFollowersFilter)

    @admin.display(description='Число рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Число подписок на рецепты')
    def favorites_count(self, user):
        return user.favorites.count()

    @admin.display(description='Число подписок на авторов')
    def followers_count(self, user):
        return user.authors.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass
    list_display = ('user', 'author')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)

    @admin.display(description='Число рецептов с продуктом')
    def recipes_count(self, product):
        return Recipe.objects.filter(ingredients__product=product).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview_color', 'slug')

    @admin.display(description='Цвет')
    def preview_color(self, tag):
        return mark_safe(
            f'<div style="background-color: {tag.color};width: 50%;height: '
            f'20px;text-align: center; padding-top: 4px;">{tag.color}</div>'
        )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'cooking_time', 'preview_image',
        'preview_ingredients', 'preview_tags'
    )
    list_filter = ('tags', CookingTimeFilter)
    search_fields = ('name',)

    @admin.display(description='Изображение')
    def preview_image(self, recipe):
        return mark_safe(f'<img src="{recipe.image}" width=50>')

    @admin.display(description='Ингредиенты')
    def preview_ingredients(self, recipe):
        return [
            f'{ingredient.product.name} {ingredient.amount} '
            f'{ingredient.product.measurement_unit}'
            for ingredient
            in recipe.ingredients.all()
        ]

    @admin.display(description='Тэги')
    def preview_tags(self, recipe):
        return [f'{tag.name}' for tag in recipe.tags.all()]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'product', 'amount')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.unregister(Group)
