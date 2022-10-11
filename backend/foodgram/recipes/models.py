from django.core.validators import MinValueValidator
from django.db import models

from users.models import FoodUser


class Tag(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    color = models.CharField(verbose_name='Цвет', max_length=7)
    slug = models.CharField(verbose_name='Идентификатор',
                            max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Product(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True)

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_product'
            )
        ]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Ingredient(models.Model):
    product = models.ForeignKey(verbose_name='Ингедиент',
                                to=Product,
                                on_delete=models.CASCADE,
                                related_name='Product',
                                null=True)
    amount = models.IntegerField(verbose_name='Количество',
                                 default=1,
                                 validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

        constraints = [
            models.UniqueConstraint(
                fields=('product', 'amount'),
                name='unique_ingredient'
            )
        ]


class Recipe(models.Model):
    author = models.ForeignKey(verbose_name='Автор',
                               to=FoodUser, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(verbose_name='Ингедиенты',
                                         to=Ingredient)
    tags = models.ManyToManyField(verbose_name='Тэги',
                                  to=Tag)
    image = models.TextField(verbose_name='Картинка')
    name = models.CharField(verbose_name='Название',
                            max_length=200)
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1, validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class ShoppingList(models.Model):
    owner = models.ForeignKey(verbose_name='Владелец',
                              to=FoodUser,
                              on_delete=models.CASCADE)
    recipes = models.ManyToManyField(verbose_name='Рецепты',
                                     to=Recipe,
                                     blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('owner',),
                name='unique_shopping_list'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favourite(models.Model):
    owner = models.ForeignKey(verbose_name='Владелец',
                              to=FoodUser,
                              on_delete=models.CASCADE)
    recipes = models.ManyToManyField(verbose_name='Рецепты',
                                     to=Recipe,
                                     related_name='recipes')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('owner',),
                name='unique_favorite_list'
            )
        ]
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
