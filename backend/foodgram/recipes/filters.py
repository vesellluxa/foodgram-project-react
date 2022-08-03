from django_filters.rest_framework import FilterSet, filters
from recipes.models import Product


class ProductFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ('name',)
