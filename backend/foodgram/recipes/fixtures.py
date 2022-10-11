import json

from recipes.models import Product


def fixture_maker():
    data = json.load(
        open('/app/recipes/ingredients.json',
             "r", encoding="utf-8"))
    for product in data:
        Product.objects.create(
            name=product['name'],
            measurement_unit=product['measurement_unit']
        )


fixture_maker()
