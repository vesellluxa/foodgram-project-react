from django.contrib import admin
from .models import Favourite, Product, Ingredient, Recipe, ShoppingList, Tag


admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Product)
admin.site.register(ShoppingList)
admin.site.register(Ingredient)
admin.site.register(Favourite)
