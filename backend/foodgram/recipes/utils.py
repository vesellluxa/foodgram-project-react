from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import ShoppingList, Ingredient, Recipe
from recipes.serializers import ShortRecipeSerializer


def generate_shop_list(request):
    shop_list = get_object_or_404(ShoppingList, owner=request.user)
    ingredients = {}
    cart = shop_list.recipes.all().values('ingredients').annotate(
        ing_amount=Count('ingredients') * F('ingredients__amount')
    )
    for ing in cart:
        ingredient = Ingredient.objects.filter(id=ing['ingredients']).first()
        name = (f'{ingredient.product.name}'
                f' ({ingredient.product.measurement_unit})')
        ingredients[name] = ing['ing_amount']
    ingredients_list = []
    for key, value in ingredients.items():
        ingredients_list.append(f'{key} - {value}, \n')
    return ingredients_list


def custom_action(self, request, pk, model):
    obj_list = model.objects.filter(
        owner=self.request.user).first()
    if obj_list is None:
        obj_list = model.objects.create(owner=self.request.user)
    recipe = Recipe.objects.filter(pk=pk).first()
    if request.method == 'POST':
        obj_list.recipes.add(recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)
    obj_list.recipes.remove(recipe)
    return Response(status=status.HTTP_204_NO_CONTENT)
