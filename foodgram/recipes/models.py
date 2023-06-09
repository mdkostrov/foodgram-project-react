from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(
        'Название',
        max_length=settings.MAX_LENGTH,
        db_index=True,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=settings.MAX_LENGTH,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_measurement_unit',
            )
        ]
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(
        'Название тега',
        unique=True,
        max_length=settings.MAX_LENGTH,
    )
    color = models.CharField(
        'Цвет тега',
        unique=True,
        max_length=settings.COLOR_NAME_LENGTH,
    )
    slug = models.SlugField(
        'Слаг тега',
        unique=True,
        max_length=settings.MAX_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LENGTH,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор рецепта',
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipe_pics/',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты рецепта',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        verbose_name='Тег рецепта',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                settings.MIN_VALUE,
                message=f'Время приготовления не может быть '
                        f'меньше {settings.MIN_VALUE} минут(-ы).'
            ),
            MaxValueValidator(
                settings.MAX_VALUE,
                message=f'Время приготовления не может быть '
                        f'больше {settings.MAX_VALUE} минут(-ы).'
            )
        ],
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связующая модель для ингредиентов в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепты',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                settings.MIN_VALUE,
                message=f'Количество не может быть '
                        f'меньше {settings.MIN_VALUE}'
            ),
            MaxValueValidator(
                settings.MAX_VALUE,
                message=f'Количество не может быть '
                        f'больше {settings.MAX_VALUE}'
            )
        ],
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_ingredient_recipe'),
        ]
        ordering = ('-pk',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return (f'{self.amount} {self.ingredient.measurement_unit}'
                f'ингредиента {self.ingredient.name} в {self.recipe.name}')


class FavoriteShoppingCart(models.Model):
    """Абстрактная модель для избранного и корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Favorite(FavoriteShoppingCart):
    """Модель для избранного"""
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite')
        ]
        default_related_name = 'favorite'
        ordering = ('-recipe',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShoppingCart):
    """Модель для корзины"""
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping')
        ]
        default_related_name = 'shopping_cart'
        ordering = ('-recipe',)
        verbose_name = 'Покупки'
        verbose_name_plural = 'Покупки'
