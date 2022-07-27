from django.shortcuts import get_object_or_404
from recipes.models import ShoppingList


def generate_shop_list(request):
    shop_list = get_object_or_404(ShoppingList, owner=request.user)
    ingredients = {}

    for recipe in shop_list.recipes.all():
        for ingredient in recipe.ingredients.all():
            name = (f'{ingredient.ingredient.name}'
                    f' ({ingredient.ingredient.measurement_unit})')
            if name in ingredients:
                ingredients[name] += ingredient.amount
            else:
                ingredients[name] = ingredient.amount

    ingredients_list = []
    for key, value in ingredients.items():
        ingredients_list.append(f'{key} - {value}, \n')

    return ingredients_list
