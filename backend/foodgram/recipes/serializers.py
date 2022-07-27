from recipes.models import Favourite, Ingredient, Ingredients, Recipe
from recipes.models import ShoppingList, Tag
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

from users.models import FoodUser
from users.serializers import FoodUserSerializer


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')

    class Meta:
        model = Tag
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
    author = FoodUserSerializer(required=False)
    cooking_time = serializers.IntegerField(required=True)
    image = Base64ImageField

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
        serializer = RepsesentRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        ret = RepsesentRecipeSerializer.to_representation(serializer, instance)
        return ret

    def validate_tags(self, value):
        for tag in value:
            if not Tag.objects.filter(pk=tag).exists():
                raise ValidationError('Not valid tag id')
        return value

    def validate_ingredients(self, values):
        for value in values:
            if not isinstance(value.get('amount'), int):
                raise ValidationError('Not valid amount of ingredient')
            if not Ingredient.objects.filter(
                    id=value.get('ingredient').get('id')).exists():
                raise ValidationError('Not valid ingredient id')
        return values

    def create(self, validated_data):
        ingredients_id = []
        ingredients_set = validated_data.pop('ingredients')
        for ingredients in ingredients_set:
            ing = Ingredient.objects.filter(
                id=ingredients.get('ingredient')['id']).first()
            if not Ingredients.objects.filter(
                    ingredient=ing, amount=ingredients.get('amount')).exists():
                ings = Ingredients.objects.create(
                    ingredient=ing, amount=ingredients.get('amount')
                )
            else:
                ings = Ingredients.objects.filter(
                    ingredient=ing, amount=ingredients.get('amount')).first()
            ingredients_id.append(ings.id)
            ings.save()
        ingredients = Ingredients.objects.filter(id__in=ingredients_id)
        tags_set = validated_data.pop('tags')
        tags = Tag.objects.filter(id__in=tags_set)
        obj = self.Meta.model.objects.create(
            author=self.context.get('request').user, **validated_data)
        obj.ingredients.set(ingredients)
        obj.tags.set(tags)
        return obj

    def update(self, instance, validated_data):
        ingredients_id = []
        ingredients_set = validated_data.pop('ingredients')
        for ingredients in ingredients_set:
            ing = Ingredient.objects.filter(
                id=ingredients.get('ingredient')['id']).first()
            if not Ingredients.objects.filter(
                    ingredient=ing, amount=ingredients.get('amount')).exists():
                ings = Ingredients.objects.create(
                    ingredient=ing, amount=ingredients.get('amount')
                )
            else:
                ings = Ingredients.objects.filter(
                    ingredient=ing, amount=ingredients.get('amount')).first()
            ingredients_id.append(ings.id)
            ings.save()
        ingredients = Ingredients.objects.filter(id__in=ingredients_id)
        instance.ingredients.set(ingredients)
        tags_set = validated_data.pop('tags')
        tags = Tag.objects.filter(id__in=tags_set)
        instance.ingredients.set(ingredients)
        instance.tags.set(tags)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        return instance

    def get_is_favorite(self, instance):
        user = self.context.get('request').user
        favorite_recipes = Favourite.objects.filter(
            owner=user).first()
        if instance in favorite_recipes.recipes.all():
            return True
        return False

    def get_is_in_shopping_cart(self, instance):
        user = self.context.get('request').user
        cart = ShoppingList.objects.filter(owner=user).first()
        if instance in cart.recipes.all():
            return True
        return False

    def get_tags(self, instance):
        return TagSerializer(instance.tags.all(), many=True)


class RepsesentRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsSerializer(many=True, required=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

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
        user = self.context.get('request').user
        favorite_recipes = Favourite.objects.filter(
            owner=user).first()
        if instance in favorite_recipes.recipes.all():
            return True
        return False

    def get_is_in_shopping_cart(self, instance):
        user = self.context.get('request').user
        cart = ShoppingList.objects.filter(owner=user).first()
        if instance in cart.recipes.all():
            return True
        return False


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
