from django.core.validators import MinValueValidator
from django.db import models
from users.models import FoodUser


class Tags(models.Model):
    name = models.CharField(max_length=200,
                            null=False, blank=False, unique=False)
    color = models.CharField(max_length=7,
                             null=False, blank=False, unique=False)
    slug = models.CharField(max_length=200,
                            null=False, blank=False, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            null=False, blank=False, unique=True)
    measurement_unit = models.CharField(max_length=200,
                                        null=False, blank=False, unique=False)


class Ingredients(models.Model):
    ingredient = models.ForeignKey(to=Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='Ingredient')
    amount = models.IntegerField(default=1,
                                 validators=[MinValueValidator(1)])


class Recipe(models.Model):
    author = models.ForeignKey(to=FoodUser, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        to=Ingredients, related_name='ingredients', blank=True)
    tags = models.ManyToManyField('Tags')
    image = models.CharField(max_length=200, blank=False)
    name = models.CharField(max_length=200, null=False,
                            blank=False, unique=False)
    text = models.TextField(null=False, blank=False, unique=False)
    cooking_time = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)])


class ShoppingList(models.Model):
    owner = models.ForeignKey(to=FoodUser, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(to=Recipe)


class Favourite(models.Model):
    owner = models.ForeignKey(to=FoodUser,
                              on_delete=models.CASCADE)
    recipes = models.ManyToManyField(to=Recipe, blank=True)
