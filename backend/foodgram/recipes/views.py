from django.http import HttpResponse
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes import serializers
from recipes.models import Favourite, Ingredient, Recipe, ShoppingList, Tag
from recipes.pagination import ApiPagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.utils import generate_shop_list, custom_action


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    pagination_class = ApiPagination
    permission_classes = (IsAuthorOrReadOnly,)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return custom_action(self, request, pk, Favourite)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return custom_action(self, request, pk, ShoppingList)

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
    serializer_class = serializers.IngredientSerializer


class TagViewset(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
