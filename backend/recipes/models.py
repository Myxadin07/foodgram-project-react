from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import Users

STR_NUMBER = 15
MAX_LENGTH = 200
MAX_HEX_LENGTH = 7
REGEX_COLOR = '^#[a-fA-F0-9]{6}$'
REGEX_ERROR = 'Введенное занчение не является HEX-кодом цвета.'
REGEX_SLUG = '^[-a-zA-Z0-9_]+$'
REGEX_SLUG_ERROR = (
    'slug введен неверно. Может состоять из латинских букв, цифр и спецсимвола _'
)


class Tags(models.Model):
    '''Модель тегов'''
    name = models.CharField(
        verbose_name='Тэг',
        max_length=MAX_LENGTH,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет в формате HEX',
        max_length=MAX_HEX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=REGEX_COLOR,
                message=REGEX_ERROR
            )
        ]
    )
    slug = models.CharField(
        verbose_name='slug',
        max_length=MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=REGEX_SLUG,
                message=REGEX_SLUG_ERROR
            )
        ]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_NUMBER]


class Ingredients(models.Model):
    '''Модель ингредиентов'''
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_NUMBER]


class Recipes(models.Model):
    '''Модель рецептов'''
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH,
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    author = models.ForeignKey(
        Users,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Список тегов',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        through='IngredientInRecipe',
        related_name='recipes',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1'),
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='recipe_unique',
            ),
        ]

    def __str__(self):
        return self.name[:STR_NUMBER]


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='ингредиент',
        related_name='ingredient_inrecipe',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        related_name='ingredientin_recipe',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество ингрединта (в граммах или штуках)',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1'),
        ]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='ingredient_in_recipe_unique',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorite_Recipes(models.Model):
    '''Модель с избранными рецептами'''
    user = models.ForeignKey(
        Users,
        verbose_name='пользователь',
        related_name='favorite_user',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        related_name='favorite_recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_unique',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Subscriptions(models.Model):
    '''Модель подписок на авторов'''

    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow_unique',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписался на пользователя {self.author}'


class Shoppingcart(models.Model):
    '''Список покупок ингредиентов по рецептам'''
    user = models.ForeignKey(
        Users,
        verbose_name='Пользователь',
        related_name='shoppingcart_user',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        related_name='shoppingcart_recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок по рецепту'
        verbose_name_plural = 'Список покупок по рецептам'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_unique',
            ),
        ]

    def __str__(self):
        return f'Список покупок по рецепту {self.recipe}'
