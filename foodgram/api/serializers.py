from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, ShoppingCart,
                            Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow

User = get_user_model()


class RecipePreviewSerializer(serializers.ModelSerializer):
    """Сериалайзер для превью рецепта в избранном и корзине"""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class MyUserSerializer(UserSerializer):
    """Кастомный сериализатор пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class SubscriptionsSerializer(UserSerializer):
    """Кастомный расширенный сериализатор
    пользователя для представления подписок
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]
        return RecipePreviewSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipe_author.all().count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели подписки на автора"""
    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message=('Подписка на этого автора уже оформлена!')
            ),
        ]

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        return SubscriptionsSerializer(
            instance.user,
            context={
                'request': self.context.get('request')
            }).data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateIngredientRecipeSerializator(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < settings.MIN_VALUE:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть положительным!'
            )
        if value > settings.MAX_VALUE:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть меньше 32000!'
            )
        return value


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта"""
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = MyUserSerializer()
    ingredients = RecipeIngredientSerializer(
        source='ingredient_in_recipe',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'ingredients',
            'text', 'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = ('author', 'tags', 'ingredients')

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = MyUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = CreateIngredientRecipeSerializator(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('author', 'name'),
                message=('Вы уже публиковали рецепт с таким именем!')
            ),
        ]

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError(
                'Выберите хотя бы один ингредиент!'
            )
        return data

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                'Выберите хотя бы один тег!'
            )
        return data

    def validate_cooking_time(self, value):
        if value < settings.MIN_VALUE:
            raise serializers.ValidationError(
                'Время приготовления не может быть нулевым или отрицательным!'
            )
        if value > settings.MAX_VALUE:
            raise serializers.ValidationError(
                'Время приготовления должно быть меньше 32000!'
            )
        return value

    @atomic
    def recipe_ingredients(self, recipe, ingredients):
        return [RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('ingredient'),
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients]

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = self.recipe_ingredients(recipe, ingredients)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
            recipe_ingredients = self.recipe_ingredients(instance, ingredients)
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает представление рецепта как после GET-запроса"""
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data
