from django.contrib import admin
from recipes.models import Favourite, Ingredient, Ingredients, Recipe
from recipes.models import ShoppingList, Tag

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(ShoppingList)
admin.site.register(Ingredients)
admin.site.register(Favourite)
