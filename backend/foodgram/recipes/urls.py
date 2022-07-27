from django.urls import include, path
from recipes.views import IngredientsViewSet, RecipeViewSet, TagViewset
from rest_framework import routers

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register('tags', TagViewset, basename='tags')

urlpatterns = [
    path('', include(router_v1.urls)),
]
