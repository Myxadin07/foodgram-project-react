from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from users.models import Users


class Tags(models.Model):
    '''Модель Тэгов'''
    name = models.CharField(
        verbose_name='Тэг',
        unique=True,
        max_length=settings.MAX_LENGTH,
    )
    color = models.CharField(
        verbose_name='Цвет тэга',
        unique=True,
        max_length=settings.MAX_HEX_LENGTH,
        validators=[
            RegexValidator(
                regex=settings.REGEX_COLOR,
                message=settings.REGEX_ERROR
            )
        ]
    )
    slug = models.CharField(
        verbose_name='slug',
        unique=True,
        max_length=settings.MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    '''Модель ингредиентов'''
    name = models.CharField(
        verbose_name='Ингредиент',
        unique=True,
        max_length=settings.MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.MAX_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return self.name


class Recipes(models.Model):
    '''Модель рецептов'''
    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        unique=True,
        max_length=settings.MAX_LENGTH,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/media/',
        verbose_name='Изображение блюда'
    )
    text = models.TextField(
        verbose_name='описание рецепта'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='tag_in_recipe',
        verbose_name='тэг рецепта',
    )
    ingredient = models.ManyToManyField(
        Ingredients,
        through='IngredientsInRecipes',
        verbose_name='Ингредиент рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(settings.MINIMUM_TIME_TO_COOK)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class IngredientsInRecipes(models.Model):
    '''Модель ингредиентов в рецепте'''
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.FloatField(
        verbose_name='количество ингредиента в рецепте',
        validators=[MinValueValidator(settings.MINIMUM_AMOUNT_VALUE)]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe_id} {self.ingredient_id}'


class Favorite(models.Model):
    '''Модель добавления в избранное'''
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='Рецепт уже есть в списке избранного'
            )
        ]

    def __str__(self):
        return f'{self.user_id} {self.recipes_id}'


class ShoppingCart(models.Model):
    '''Модель корзины'''
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='users_shopping_cart',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_cart'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='Рецепт уже есть в списке покупок',
            ),
        ]

    def __str__(self):
        return f'{self.user_id}{self.recipes_id}'
