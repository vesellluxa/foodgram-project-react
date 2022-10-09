from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes.filters import ProductFilter
from recipes.models import Favourite, Product, Recipe, ShoppingList, Tag
from recipes.pagination import ApiPagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (ProductSerializer, RecipeSerializer,
                                 TagSerializer)
from recipes.utils import generate_shop_list, custom_action


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = ApiPagination
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        if self.request.GET.get('is_favorited'):
            queryset = Favourite.objects.filter(
                owner=self.request.user).first().recipes.all()
        else:
            queryset = Recipe.objects.all()
        if self.request.GET.get('tags'):
            queryset = queryset.filter(
                tags__in=Tag.objects.filter(
                    name__in=self.request.GET.getlist('tags')
                )
            ).distinct()
        return queryset

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


class ProductViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = None


class TagViewset(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
