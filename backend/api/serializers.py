from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from djoser.serializers import UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredients, Tags, Recipes, ShoppingCart,
    IngredientsInRecipes, Favorite
)
from users.models import Users


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    '''Сериализатор пользователя'''
    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        '''Подписан ли текущий пользователь на запрашимаего пользователя'''
        request = self.context.get('request')
        if request is not None:
            current_user = request.user
            if current_user.is_authenticated:
                return obj in current_user.subscriptions.filter(pk=obj.pk)
            return False


class SetPasswordSerializer(serializers.Serializer):
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
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientsInRecipes


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        print('дошло')
        current_user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data, author=current_user)
        for ingredient in ingredients:
            amount = ingredient.pop("amount")
            ingredient = get_object_or_404(Ingredients, id=ingredient["id"])
            IngredientsInRecipes.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredient.clear()
        ingredient_counts = {}
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if ingredient_id in ingredient_counts:
                ingredient_counts[ingredient_id] += amount
            else:
                ingredient_counts[ingredient_id] = amount
        create_ingredients = [
            IngredientsInRecipes(
                recipe=instance,
                ingredient_id=ingredient_id,
                amount=amount
            )
            for ingredient_id, amount in ingredient_counts.items()
        ]
        IngredientsInRecipes.objects.bulk_create(create_ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data

    def validate(self, data):
        if data.get('cooking_time') < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не меньше одной минуты!')
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients or len(ingredients) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент!')
        if not tags or len(tags) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один тег!')
        for ingredient in ingredients:
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть не меньше одного!')
        return data


class ReadRecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = IngredientsInRecipes.objects.filter(recipe=obj)
        return ReadRecipeIngredientSerializer(ingredients, many=True).data
    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return Favorite.objects.filter(
                    user=current_user, recipes=obj.id).exists()
            return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return ShoppingCart.objects.filter(
                    user=current_user, recipes=obj.id).exists()
            return False

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


class SerializerForCreatedRecipes(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipes
