from collections import OrderedDict

from recipes.models import (Favourite, Ingredient, Ingredients, Recipe,
                            ShoppingList, Tags)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import FoodUser
from users.serializers import FoodUserSerializer


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    color = serializers.CharField(required=False)
    slug = serializers.CharField(required=False)
    id = serializers.IntegerField(source='pk')

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    id = serializers.IntegerField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsSerializer(many=True, required=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.ListField(required=True)
    # tags = TagSerializer(many=True)
    author = FoodUserSerializer(required=False)
    cooking_time = serializers.IntegerField(required=True)
    image = serializers.CharField(required=True)

    # name = serializers.

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time')

    def to_representation(self, instance):
        if isinstance(instance, OrderedDict):
            return super(RecipeSerializer, self).to_representation(instance)
        if self.fields.get('tags') is None:
            return super(RecipeSerializer, self).to_representation(instance)
        else:
            self.fields.pop('tags')
            ret = super(RecipeSerializer, self).to_representation(instance)
            ret.update({'tags': self.get_tags(instance).data})
            return ret

    def validate_tags(self, value):
        return Tags.objects.filter(id__in=value)

    def validate_ingredients(self, value):
        ingredients_id = []
        for value in value:
            if not isinstance(value.get('amount'), int):
                raise ValidationError('Not valid amount of ingredient')
            ing = Ingredient.objects.filter(
                id=value.get('ingredient').get('id')).first()
            if ing is None:
                raise ValidationError('Not valid ingredient')
            ings = Ingredients.objects.get_or_create(
                ingredient=ing, amount=value.get('amount'))
            ingredients_id.append(ings.id)
            ings.save()
        value = Ingredients.objects.filter(id__in=ingredients_id)
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        obj = self.Meta.model.objects.create(
            author=self.context.get('request').user, **validated_data)
        obj.ingredients.set(ingredients)
        obj.tags.set(tags)
        return obj

    def get_is_favorite(self, instance):
        user = self.context.get('request').user
        favorite_recipes, is_created = Favourite.objects.get_or_create(
            owner=user)
        if instance in favorite_recipes.recipes.all():
            return True
        return False

    def get_is_in_shopping_cart(self, instance):
        user = self.context.get('request').user
        cart, is_created = ShoppingList.objects.get_or_create(owner=user)
        if instance in cart.recipes.all():
            return True
        return False

    def get_tags(self, instance):
        return TagSerializer(instance.tags.all(), many=True)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(FoodUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = FoodUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count')

    def get_recipes(self, value):
        recipe_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipe_limit:
            recipes = Recipe.objects.filter(author=value)[:int(recipe_limit)]
            serializer = ShortRecipeSerializer(recipes, many=True)
            return serializer.data
        recipes = Recipe.objects.filter(author=value)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, value):
        count = Recipe.objects.filter(author=value).count()
        return count
