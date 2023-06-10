from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import (IngredientInRecipe, Ingredients, Recipes,
                            Subscriptions)


def add_or_delete_recipes_view(
  request, model, recipeminifiedserializer, **kwargs
):

    recipe_id = kwargs['pk']
    user = request.user
    recipe_obj = get_object_or_404(Recipes, pk=recipe_id)
    data = {
        "id": recipe_id,
        "name": recipe_obj.name,
        "image": recipe_obj.image,
        "cooking_time": recipe_obj.cooking_time,
    }

    if request.method == 'POST':
        serializer = recipeminifiedserializer(
            sample=data,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            model.objects.create(
                user=user, recipe_id=recipe_id
            )
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

    if request.method == 'DELETE':
        get_object_or_404(
            model,
            user=user,
            recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


def boolean_serializers_item(self, model, obj):

    user = self.context.get('request').user

    if user.is_anonymous:
        return False

    if model == Subscriptions:
        if model.objects.filter(
            author_id=obj.id,
            user=user
        ).exists():
            return True
        return False

    if model.objects.filter(
        recipe_id=obj.id,
        user=user
    ).exists():
        return True
    return False


def create_or_update_recipes(validated_data, author=None, sample=None):

    tags = validated_data.pop('tags')
    ingredients = validated_data.pop('ingredientin_recipe')

    if sample is None:
        recipe = Recipes.objects.create(author=author, **validated_data)
    else:
        recipe = sample

    recipe.tags.set(tags)

    IngredientInRecipe.objects.bulk_create([
        IngredientInRecipe(
            recipe=recipe,
            amount=ingredient.get('amount'),
            ingredient=Ingredients.objects.get(
                id=ingredient.get('id')
            ),
        ) for ingredient in ingredients
    ])

    return recipe
