from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from users.models import Users


MAX_LENGTH = 256
MAX_HEX_LENGTH = 7
REGEX_COLOR = '^#[a-fA-F0-9]{6}$'
REGEX_ERROR = 'Введенное занчение не является HEX-кодом цвета.'
MINIMUM_TIME_TO_COOK = 1


class Tags(models.Model):
    name = models.CharField(
        verbose_name='Тэг',
        unique=True,
        max_length=MAX_LENGTH,
    )
    color = models.CharField(
        verbose_name='Цвет тэга',
        unique=True,
        max_length=MAX_HEX_LENGTH,
        validators=[
            RegexValidator(
                regex=REGEX_COLOR,
                message=REGEX_ERROR
            )
        ]
    )
    slug = models.CharField(
        verbose_name='slug',
        unique=True,
        max_length=MAX_LENGTH,
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
        max_length=MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='author_of_recipe',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        unique=True,
        max_length=MAX_LENGTH,
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
        validators=[MinValueValidator(MINIMUM_TIME_TO_COOK)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания рецепта'
    )
    favorites = models.ManyToManyField(
        to=Users,
        related_name='favorites_for_users'
    )

    class Meta:
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class IngredientsInRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipes',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipes'
    )
    amount = models.FloatField(
        verbose_name='количество ингредиента в рецепте'
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
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user_id} {self.recipes_id}'


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='users_shopping_cart',
    )
    recipes = models.ManyToManyField(
        Recipes,
        related_name='recipe_shopping_cart'
    )

    class Meta:
        verbose_name = 'Корзина покупок',
        verbose_name_plural = 'Корзины покупок',

    def __str__(self):
        return f'{self.user_id}{self.recipes_id}'
