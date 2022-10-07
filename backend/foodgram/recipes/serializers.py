from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favourite, Product, Ingredient, Recipe,
                            ShoppingList, Tag)
from users.models import FoodUser
from users.serializers import FoodUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='product.name')
    id = serializers.IntegerField(source='product.id')
    measurement_unit = serializers.ReadOnlyField(
        source='product.measurement_unit')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.ListField(required=True)
    author = FoodUserSerializer(required=False)
    cooking_time = serializers.IntegerField(required=True)
    image = serializers.CharField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time')

    def to_representation(self, instance):
        serializer = RepsesentRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def validate_tags(self, value):
        for tag in value:
            if not Tag.objects.filter(pk=tag).exists():
                raise ValidationError('Not valid tag id')
        return value

    def validate_ingredients(self, values):
        products = []
        for value in values:
            if not isinstance(value.get('amount'), int):
                raise ValidationError('Not valid amount of product')
            if not Product.objects.filter(
                    id=value.get('product').get('id')).exists():
                raise ValidationError('Not valid product id')
            products.append(value.get('product').get('id'))
        if len(products) != len(set(products)):
            raise ValidationError('Some products are duplicated')
        return values

    def create(self, validated_data):
        ingredients = self.get_ingredients(validated_data.pop('ingredients'))
        tags = Tag.objects.filter(id__in=validated_data.pop('tags'))
        obj = self.Meta.model.objects.create(
            author=self.context.get('request').user, **validated_data)
        obj.ingredients.set(ingredients)
        obj.tags.set(tags)
        return obj

    def update(self, instance, validated_data):
        instance.ingredients.set(
            self.get_ingredients(validated_data.pop('ingredients')))
        instance.tags.set(
            Tag.objects.filter(id__in=validated_data.pop('tags')))
        instance = super().update(
            validated_data=validated_data, instance=instance)
        return instance

    def get_is_favorited(self, instance):
        return Favourite.objects.filter(
            owner=self.context.get('request').user,
            recipes=instance).exists()

    def get_is_in_shopping_cart(self, instance):
        return ShoppingList.objects.filter(
            owner=self.context.get('request').user,
            recipes=instance).exists()

    def get_tags(self, instance):
        return TagSerializer(instance.tags.all(), many=True)

    def get_ingredients(self, data):
        ingredients_id = []
        for ingredient in data:
            product = Product.objects.get(id=ingredient.get('product')['id'])
            if not Ingredient.objects.filter(
                    product=product,
                    amount=ingredient.get('amount')).exists():
                ing = Ingredient.objects.create(
                    product=product,
                    amount=ingredient.get('amount')
                )
            else:
                ing = Ingredient.objects.filter(
                    product=ingredient.get('product')['id'],
                    amount=ingredient.get('amount')).first()
            ingredients_id.append(ing.id)
        return Ingredient.objects.filter(id__in=ingredients_id)


class RepsesentRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = FoodUserSerializer()

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

    def get_is_favorite(self, instance):
        return Favourite.objects.filter(
                owner=self.context.get('request').user,
                recipes=instance).exists()

    def get_is_in_shopping_cart(self, instance):
        return ShoppingList.objects.filter(
                owner=self.context.get('request').user,
                recipes=instance).exists()


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
        return Recipe.objects.filter(author=value).count()
