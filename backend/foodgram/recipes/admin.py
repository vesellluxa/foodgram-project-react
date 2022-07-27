from django.contrib import admin
from recipes.models import (Favourite, Ingredient, Ingredients, Recipe,
                            ShoppingList, Tags)

# Register your models here.
admin.site.register(Tags)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(ShoppingList)
admin.site.register(Ingredients)
admin.site.register(Favourite)
