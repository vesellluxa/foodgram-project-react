import json

from .models import Product


def fixture_maker():
    data = json.load(
        open('/Users/a1/PycharmProjects/finalgovna/'
             'foodgram-project-react/data/ingredients.json',
             "r", encoding="utf-8"))
    for product in data:
        Product.objects.create(
            name=product['name'],
            measurement_unit=product['measurement_unit']
        )


fixture_maker()
