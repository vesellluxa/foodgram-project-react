from django.core.validators import MinValueValidator
from django.db import models

from users.models import FoodUser


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=200,
        unique=True)

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        unique=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Ingredients(models.Model):
    ingredient = models.ForeignKey(verbose_name='Ингедиент',
                                   to=Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='Ingredient')
    amount = models.IntegerField(verbose_name='Количество',
                                 default=1,
                                 validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(verbose_name='Автор',
                               to=FoodUser, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(verbose_name='Ингедиенты',
                                         to=Ingredients,
                                         related_name='recipes',
                                         blank=True)
    tags = models.ManyToManyField(verbose_name='Тэги',
                                  to=Tag)
    image = models.CharField(verbose_name='Картинка',
                             max_length=200, blank=False)
    name = models.CharField(verbose_name='Название',
                            max_length=200, unique=False)
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1, validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class ShoppingList(models.Model):
    owner = models.ForeignKey(verbose_name='Владелец',
                              to=FoodUser,
                              on_delete=models.CASCADE)
    recipes = models.ManyToManyField(verbose_name='Рецепты',
                                     to=Recipe)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('owner', ),
                name='unique_shopping_list'
            ),
            models.UniqueConstraint(
                fields=('recipes', ),
                name='unique_recipes_in_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favourite(models.Model):
    owner = models.ForeignKey(verbose_name='Владелец',
                              to=FoodUser,
                              on_delete=models.CASCADE)
    recipes = models.ManyToManyField(verbose_name='Рецепты',
                                     to=Recipe, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('owner', ),
                name='unique_favorite_list'
            )
        ]
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
