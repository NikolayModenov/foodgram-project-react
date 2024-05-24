from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from recipe.validators import validate_username

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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user', 'author')

    def __str__(self):
        return f'{self.user.last_name[:30]} {self.user.first_name[:30]}'


class Ingredient(models.Model):

    name = models.CharField('Название', max_length=CHARFIELD_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=CHARFIELD_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', 'measurement_unit')

    def __str__(self):
        return f'{self.name[:30]} {self.measurement_unit[:30]}'


class Tag(models.Model):

    name = models.CharField(
        'Название', max_length=CHARFIELD_MAX_LENGTH, unique=True
    )
    color = models.CharField(
        'Код цвета', max_length=COLOR_MAX_LENGTH, validators=[RegexValidator(
            regex=r'^\#([a-fA-F0-9]{6})$',
            code='Указанный цвет не соответствует HEX кодировке.',
            message='Введите цвет соответствующий HEX кодировке.'
        )],
        unique=True
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
        verbose_name='Тэги'
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
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name[:30]}'


class RecipeSubscribeBase(models.Model):

    user = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user.last_name[:30]} {self.user.first_name[:30]}'


class Favorite(RecipeSubscribeBase):

    class Meta(RecipeSubscribeBase.Meta):
        verbose_name = 'Подписка на рецепт'
        verbose_name_plural = 'Подписки на рецепты'


class Product(models.Model):

    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        default_related_name = 'products'
        ordering = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.ingredient.name[:30]} {self.recipe.name[:30]}'


class ShoppingCart(RecipeSubscribeBase):

    class Meta(RecipeSubscribeBase.Meta):
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Список корзин покупок'
