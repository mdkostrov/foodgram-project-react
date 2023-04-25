from django.db import models
from django.core.validators import MinValueValidator
from django.template.defaultfilters import slugify

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        unique=True,
        max_length=200,
        db_index=True,
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения',
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
    name = models.CharField(
        'Название тега',
        unique=True,
        max_length=200,
        help_text='Введите тег',
    )
    color = models.CharField(
        'Цвет тега',
        unique=True,
        max_length=7,
        help_text='Укажите цвет тега',
    )
    slug = models.SlugField(
        'Слаг тега',
        unique=True,
        max_length=200,
        blank=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Автоматически генерирует слаг, если он не указан."""
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        help_text='Введите название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта',
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipe_pics/',
        help_text='Загрузить фото рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты рецепта',
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Опишите ваш рецепт здесь',
    )
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        verbose_name='Тег рецепта',
        related_name='recipe',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
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
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_ingredient_recipe'),
        ]
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')


class FavoriteShoppingCart(models.Model):
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
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite')
        ]
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShoppingCart):
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping')
        ]
        default_related_name = 'shopping_cart'
        verbose_name = 'Покупки'
        verbose_name_plural = 'Покупки'
