from django.http import HttpResponse
from recipes.models import Favourite, Ingredient, Recipe, ShoppingList, Tags
from recipes.pagination import ApiPagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (IngredientSerializer, RecipeSerializer,
                                 ShortRecipeSerializer, TagSerializer)
from recipes.utils import generate_shop_list
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = ApiPagination
    permission_classes = (IsAuthorOrReadOnly, )

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        favorite_list = Favourite.objects.get_or_create(
            owner=self.request.user)
        recipe = Recipe.objects.filter(pk=pk).first()
        if request.method == 'POST':
            favorite_list.recipes.add(recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        favorite_list.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        shopping_cart = ShoppingList.objects.get_or_create(
            owner=self.request.user)
        recipe = Recipe.objects.filter(pk=pk).first()
        if request.method == 'POST':
            shopping_cart.recipes.add(recipe)
            return Response(data={"id": recipe.pk,
                                  "name": recipe.name,
                                  "image": recipe.image,
                                  "cooking_time": recipe.cooking_time},
                            status=status.HTTP_201_CREATED)
        shopping_cart.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        result = generate_shop_list(request)
        filename = "ingredients.txt"
        response = HttpResponse(result, content_type="text/plain")
        response["Content-Disposition"] = "attachment; filename={0}".format(
            filename)
        return response


class IngredientsViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewset(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
