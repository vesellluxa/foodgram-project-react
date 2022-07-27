from django.urls import include, path
from recipes.views import IngredientsViewSet, RecipeViewSet, TagViewset
from rest_framework import routers

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('tags', TagViewset, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
