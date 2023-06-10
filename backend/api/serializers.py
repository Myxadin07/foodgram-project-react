from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite_Recipes, IngredientInRecipe, Ingredients,
                            Recipes, Shoppingcart, Subscriptions, Tags)

from .utils import boolean_serializers_item, create_or_update_recipes

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    '''Сериализатор пользователя'''
    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        '''Подписан ли текущий пользователь на запрашимаего пользователя'''
        return boolean_serializers_item(self, Subscriptions, obj)


class TagsSerializer(serializers.ModelSerializer):
    '''Сериализатор Tags'''

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов'''

    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsInRecipesSerializers(serializers.ModelSerializer):
    '''Сериализатор для связи рецепт-игредиент-количество'''
    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    '''Сериализатор c рецептами'''
    image = Base64ImageField(
        required=False, allow_null=True
    )

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('name', 'image', 'cooking_time',)


class RecipesSerializer(RecipeMinifiedSerializer):
    '''Сериализатор рецептов для чтения данных'''
    author = CustomUserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeMinifiedSerializer.Meta):
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorite', 'is_in_shopping_cart', 'text',
        ) + RecipeMinifiedSerializer.Meta.fields

    def get_ingredients(self, obj):
        '''Игредиенты рецепта с необходимым количеством'''
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_inrecipe__amount')
        )

    def get_is_favorite(self, obj):
        '''Находится ли рецепт в списке избранных'''
        return boolean_serializers_item(self, Favorite_Recipes, obj)

    def get_is_in_shopping_cart(self, obj):
        '''Находится ли рецепт в списке покупок'''
        return boolean_serializers_item(self, Shoppingcart, obj)


class AddRecipesSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания и редактирования рецептов'''
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tags.objects.all()
    )
    ingredients = IngredientsInRecipesSerializers(
        source='ingredient_in_recipe', many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'image', 'name', 'text', 'cooking_time',
        )

    def validate_tags(self, data):
        '''Проверка на выбор хотя бы одного Tags'''
        tags = self.initial_data.get('tags')

        if len(tags) == 0:
            raise serializers.ValidationError(
                'Выберите хотя бы 1 Tags'
            )

        return data

    def validate_ingredients(self, data):
        '''Проверка на наличие хотя бы одного ингредиента'''
        ingredients = self.initial_data.get('ingredients')

        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Выберите хотя бы 1 ингредиент из списка.'
            )

        ingredients_id = []
        for ingredient in ingredients:

            if ingredient.get('id') in ingredients_id:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторятся'
                    'Проверьте свой рецепт.'
                )
            if ingredient.get('amount') in (None, 0):
                raise serializers.ValidationError(
                    'Количество ингредиента обязательно для заполнения'
                    'Минимальное значение 1.'
                )

            ingredients_id.append(ingredient.get('id'))

        return data

    def create(self, validated_data):
        '''Создание нового рецепта'''
        author = self.context.get('request').user
        name_recipe = self.validated_data.get('name')

        if Recipes.objects.filter(
            author=author,
            name=name_recipe
        ).exists():
            raise serializers.ValidationError(
                f'У Вас уже есть рецепт с именем {name_recipe}. '
                'Проверьте свой рецепт.'
            )

        return create_or_update_recipes(validated_data, author=author)

    def update(self, sample, validated_data):
        '''Обновление рецепта'''
        sample.name = validated_data.get('name', sample.name)
        sample.text = validated_data.get('text', sample.text)
        sample.image = validated_data.get('image', sample.image)
        sample.cooking_time = validated_data.get(
            'cooking_time', sample.cooking_time
        )

        old_ingredients = IngredientInRecipe.objects.filter(
            recipe_id=sample.id
        )
        old_ingredients.delete()
        create_or_update_recipes(validated_data, sample=sample)

        sample.save()
        return sample

    def to_representation(self, sample):
        '''Переопределение ответа'''
        context = {'request': self.context.get('request')}
        serializer = RecipesSerializer(
            sample=sample,
            context=context
        )
        return serializer.data


class SubscriptionsSerializer(CustomUserSerializer):
    '''Сериализатор подписок'''
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        )
        read_only_fields = ('email', 'username',)

    def validate(self, data):
        '''Проверка подписок пользователя'''
        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscriptions.objects.filter(
            user=user, author=author
        ).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на {author}.'
            )
        return data

    def get_recipes(self, obj):
        '''
        Cписок рецептов автора, на которого подписан пользователь
        '''
        limit = self.context.get('request')._request.GET.get('recipes_limit')
        recipes_data = Recipes.objects.filter(
            author=obj.id
        )
        if limit:
            recipes_data = recipes_data[:int(limit)]

        serializer = RecipeMinifiedSerializer(
            data=recipes_data,
            many=True
        )
        serializer.is_valid()
        return serializer.data

    def get_recipes_count(self, obj):
        '''Количество рецептов у избранного автора'''
        return obj.recipes.count()
