# Generated by Django 3.2 on 2023-05-10 13:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'default_related_name': 'favorite', 'ordering': ('-recipe',), 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ('-pk',), 'verbose_name': 'Количество ингредиента', 'verbose_name_plural': 'Количество ингредиентов'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shopping_cart', 'ordering': ('-recipe',), 'verbose_name': 'Покупки', 'verbose_name_plural': 'Покупки'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не может быть меньше 1 минут(-ы).'), django.core.validators.MaxValueValidator(32000, message='Время приготовления не может быть больше 32000 минут(-ы).')], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Количество не может быть меньше 1'), django.core.validators.MaxValueValidator(32000, message='Количество не может быть больше 32000')], verbose_name='Количество'),
        ),
    ]
