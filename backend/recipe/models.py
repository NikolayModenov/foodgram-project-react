from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH = 150


class FoodgramUser(AbstractUser):
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=MAX_LENGTH)
    last_name = models.CharField('last name', max_length=MAX_LENGTH)
    # is_subscribed = models.BooleanField('is_subscribed')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


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


class Product(models.Model):
    name = models.CharField(max_length=16)
    measurement_unit = models.CharField(max_length=16)

    class Meta:
        # verbose_name = 'Произведение'
        # verbose_name_plural = 'Произведения'
        default_related_name = 'product'


class Tag(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    slug = models.SlugField(max_length=100, unique=True)


# class RecipeIngredient(models.Model):
#     amount = models.FloatField()
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE
#     )
#     ingredient = models.ForeignKey(
#         Ingredient,
#         on_delete=models.CASCADE
#     )


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodgramUser,
        # related_name='recipe',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=16)
    image = models.ImageField(
        upload_to='api/images/',
        null=True,
        default=None
    )
    text = models.TextField()
    # ingredients = models.ManyToManyField(
    #     Product, through='Ingredient'
    #     # on_delete=models.CASCADE
    # )
    # ingredients = models.ForeignKey(
    #     RecipeIngredient,
    #     on_delete=models.CASCADE
    # )
    # ingredients = models.ForeignKey(
        
    #     Ingredient,
    #     on_delete=models.SET_NULL, null=True, blank=True,
    # )
    tags = models.ManyToManyField(
        Tag,
        related_name='tag'
        # verbose_name='Жанр произведения',
    )
    cooking_time = models.IntegerField()

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'recipes'


# class RecipeTag(models.Model):
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE
#     )
#     tag = models.ForeignKey(
#         Tag,
#         on_delete=models.CASCADE
#     )


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
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'ingredients'
