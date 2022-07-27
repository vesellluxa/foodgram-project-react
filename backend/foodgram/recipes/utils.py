from django.db.models import Count
from django.shortcuts import get_object_or_404
from recipes.models import ShoppingList, Ingredients


def generate_shop_list(request):
    shop_list = get_object_or_404(ShoppingList, owner=request.user)
    ingredients = {}
    cart = shop_list.recipes.all().values(
        'ingredients').annotate(Count('ingredients'))
    for id in cart:
        ingredient = Ingredients.objects.filter(id=id['ingredients']).first()
        name = (f'{ingredient.ingredient.name}'
                f' ({ingredient.ingredient.measurement_unit})')
        ingredients[name] = ingredient.amount * id['ingredients__count']
    ingredients_list = []
    for key, value in ingredients.items():
        ingredients_list.append(f'{key} - {value}, \n')
    return ingredients_list
