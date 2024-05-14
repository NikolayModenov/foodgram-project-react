from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from recipe.validators import (
    validate_amount, validate_hex_color, validate_username
)

USER_CHARFIELD_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
CHARFIELD_MAX_LENGTH = 200
COLOR_MAX_LENGTH = 7


class FoodgramUser(AbstractUser):

    email = models.EmailField(
        'Адрес электронной почты', unique=True, max_length=EMAIL_MAX_LENGTH
    )
    first_name = models.CharField('Имя', max_length=USER_CHARFIELD_MAX_LENGTH)
    last_name = models.CharField(
        'Фамилия', max_length=USER_CHARFIELD_MAX_LENGTH
    )
    username = models.CharField(
        'Имя пользователя', max_length=USER_CHARFIELD_MAX_LENGTH, unique=True,
        validators=[validate_username]
    )
    password = models.CharField('Пароль', max_length=USER_CHARFIELD_MAX_LENGTH)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return f'{self.last_name[:30]} {self.first_name[:30]}'


class Follow(models.Model):

    user = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='users',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        FoodgramUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='authors', verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_author'
            )
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('user', 'author')

    def __str__(self):
        return f'{self.user.last_name[:30]} {self.user.first_name[:30]}'


class Product(models.Model):

    name = models.CharField('Название', max_length=CHARFIELD_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Еденица имзмерения', max_length=CHARFIELD_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name', 'measurement_unit')

    def __str__(self):
        return f'{self.name[:30]} {self.measurement_unit[:30]}'


class Tag(models.Model):

    name = models.CharField('Название', max_length=CHARFIELD_MAX_LENGTH)
    color = models.CharField(
        'Цвет', max_length=COLOR_MAX_LENGTH, validators=[validate_hex_color]
    )
    slug = models.SlugField(
        'Метка', max_length=CHARFIELD_MAX_LENGTH, unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('slug',)

    def __str__(self):
        return f'{self.name[:30]}'


class Recipe(models.Model):

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=CHARFIELD_MAX_LENGTH)
    image = models.ImageField(
        'Изображение',
        upload_to='api/images/',
    )
    text = models.TextField('Описание')
    tags = models.ManyToManyField(
        Tag,
        related_name='tag',
        verbose_name='Тэг'
    )
    cooking_time = models.IntegerField(
        'Время приготовления', validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.name[:30]}'


class FavoriteShoppingCartBase(models.Model):

    user = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.last_name[:30]} {self.user.first_name[:30]}'


class Favorite(FavoriteShoppingCartBase):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class Ingredient(models.Model):

    amount = models.FloatField('Количество', validators=[validate_amount])
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Игредиенты'
        default_related_name = 'ingredients'
        ordering = ('recipe', 'product')

    def __str__(self):
        return f'{self.product.name[:30]} {self.recipe.name[:30]}'


class ShoppingCart(FavoriteShoppingCartBase):

    class Meta:
        verbose_name = 'Рецепт для покупок'
        verbose_name_plural = 'Рецепты для покупок'
        default_related_name = 'shopping_carts'
