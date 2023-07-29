from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from djoser.serializers import UserSerializer
from rest_framework import serializers, exceptions
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredients, Tags, Recipes, ShoppingCart,
    IngredientsInRecipes, Favorite
)
from users.models import Users, Follow


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    '''Сериализатор пользователя'''
    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        return Follow.objects.filter(
            author=obj,
            user=self.context.get('request').user
        ).exists()


class SetPasswordSerializer(serializers.Serializer):
    '''Сериалайзер изменения пароля'''
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TagsSerializer(serializers.ModelSerializer):
    '''Сериализатор Tags'''
    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов'''
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipesSerializer(serializers.ModelSerializer):
    '''Сериализатор рецептов'''
    amount = serializers.FloatField()

    class Meta:
        fields = '__all__'


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    '''Для показа ингредиентов и количества в рецепте'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    '''Создание ингредиентов для рецепта связующий сериализатор'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'amount',)


class CreateRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор создания рецепта'''
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
    )
    ingredients = CreateRecipeIngredientSerializer(
        many=True
    )

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'ingredients', 'author', 'image',
            'name', 'text', 'cooking_time',
        )
        read_only_fields = ('author',)

    def create_ingredients(self, recipe, ingredients):
        recipe_ingredients = [
            IngredientsInRecipes(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients
        ]
        IngredientsInRecipes.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        current_user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        new_recipe = Recipes.objects.create(
            author=current_user,
            **validated_data
        )
        new_recipe.tags.set(tags)
        self.create_ingredients(new_recipe, ingredients)
        return new_recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        IngredientsInRecipes.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data

    def validate_ingredients(self, data):
        ingredients = data
        if not ingredients or len(ingredients) == 0:
            raise exceptions.ValidationError(
                {'ingredients': settings.MIN_INGREDIENT_AMOUNT_ERROR}
            )

        ingredients_list = []
        ingredients = self.initial_data.get('ingredients')
        for item in ingredients:
            if item['id'] in ingredients_list:
                raise exceptions.ValidationError(
                    {'ingredients': settings.DUPLICATE_INGREDIENT_ERROR}
                )
            ingredients_list.append(item['id'])
            if int(item['amount']) <= 0:
                raise exceptions.ValidationError(
                    {'amount': settings.MIN_INGREDIENT_AMOUNT_ERROR}
                )
        return data

    def validate_tags(self, data):
        tags = data
        if not tags or len(tags) == 0:
            raise exceptions.ValidationError(
                {'tags': settings.TAG_ERROR}
            )
        return data

    def validate_cooking_time(self, data):
        cooking_time = data
        if cooking_time < 1:
            raise exceptions.ValidationError(
                settings.MIN_COOKING_TIME_ERROR
            )
        return data


class ReadRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор показа рецепта, добавлен в избранное или в корзину'''
    ingredients = serializers.SerializerMethodField()
    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'ingredients', 'author', 'name', 'image',
            'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart',
        )
        read_only_fields = (
            'id', 'tags', 'ingredients', 'author', 'name', 'image', 'text',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientsInRecipes.objects.filter(recipe=obj)
        return ReadRecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        current_user = request.user
        if current_user.is_authenticated:
            return Favorite.objects.filter(
                user=current_user, recipes=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        current_user = request.user
        if current_user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=current_user, recipes=obj.id).exists()
        return False


class SerializerForCreatedRecipes(serializers.ModelSerializer):
    '''Сериализатор короткого рецепта, для показа при успешном создании'''
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipes


class SubscriptionSerializer(serializers.ModelSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'author',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
            serializer = SerializerForCreatedRecipes(
                instance=recipes,
                many=True,
                context=self.context,
            )
            return serializer.data
        return []

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(
            user=request.user, author=obj.pk
        ).exists()
