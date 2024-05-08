from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH = 150


class FoodgramUser(AbstractUser):

    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=MAX_LENGTH)
    last_name = models.CharField('last name', max_length=MAX_LENGTH)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'user'
        ordering = ('email',)

    def __str__(self):
        return f'{self.last_name[:30]} {self.first_name[:30]}'


class Follow(models.Model):

    user = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        FoodgramUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            )
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('user', 'following')

    def __str__(self):
        return f'{self.user[:30]}'


class Product(models.Model):

    name = models.CharField(max_length=16)
    measurement_unit = models.CharField(max_length=16)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        default_related_name = 'product'
        ordering = ('name', 'measurement_unit')

    def __str__(self):
        return f'{self.name[:30]}'


class Tag(models.Model):

    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        default_related_name = 'tags'
        ordering = ('slug',)

    def __str__(self):
        return f'{self.name[:30]}'


class Recipe(models.Model):

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=16)
    image = models.ImageField(
        upload_to='api/images/',
    )
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        related_name='tag'
    )
    cooking_time = models.IntegerField()
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


class Favorite(models.Model):

    user = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='favorite'
    )
    favorite_recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorite'
        ordering = ('user', 'favorite_recipe')

    def __str__(self):
        return f'{self.user.last_name[:30]} {self.user.first_name[:30]}'


class Ingredient(models.Model):

    amount = models.FloatField()
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Игредиенты'
        default_related_name = 'ingredients'
        ordering = ('recipe', 'product')

    def __str__(self):
        return f'{self.product.name[:30]} {self.recipe.name[:30]}'


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Покупки'
        default_related_name = 'shopping_cart'
        ordering = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.last_name[:30]} {self.user.first_name[:30]}'
