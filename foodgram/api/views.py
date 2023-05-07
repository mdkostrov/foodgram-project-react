from django.db.models import F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from recipes.models import (Favorite, Ingredient,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User
from .filters import RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipePreviewSerializer, RecipeWriteSerializer,
                          RecipeReadSerializer, TagSerializer,
                          SubscriptionsSerializer)


class MyUserViewSet(UserViewSet):
    """Кастомный вьюсет пользователя"""
    pagination_class = FoodgramPagination
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action in ('subscribe', 'subscriptions'):
            return [IsAuthenticated()]
        else:
            return super().get_permissions()

    @action(detail=True, methods=['post'],
            pagination_class=FoodgramPagination)
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        if request.user == author:
            return Response({
                'error': 'Нельзя подписываться на самого себя!'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=request.user, following=author).exists():
            return Response({
                'errors': 'Подписка уже оформлена!'
            }, status=status.HTTP_400_BAD_REQUEST)
        data = Follow.objects.create(user=request.user, following=author)
        serializer = FollowSerializer(
            data=data, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        if Follow.objects.filter(user=request.user, following=author).exists():
            get_object_or_404(
                Follow,
                user=request.user,
                following=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Подписка уже отменена!'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, pagination_class=FoodgramPagination)
    def subscriptions(self, request, pk=None):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ModelViewSet):
    """Вьюсет ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(
                Q(name__istartswith=name) | Q(name__icontains=name)
            )
        return queryset


class TagViewSet(ModelViewSet):
    """Вьюсет тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов"""
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = FoodgramPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if instance.exists():
                return Response({
                    'errors': 'Рецепт уже находится в избранном!'
                }, status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipePreviewSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not instance.exists():
                return Response({
                    'errors': 'Рецепт уже удален из избранного!'
                }, status=status.HTTP_400_BAD_REQUEST)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if instance.exists():
                return Response({
                    'errors': 'Рецепт уже находится в списке покупок!'
                }, status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipePreviewSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not instance.exists():
                return Response({
                    'errors': 'Рецепт отсутствовал в списке покупок!'
                }, status=status.HTTP_400_BAD_REQUEST)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(total=Sum('ingredients_list__amount')).order_by('-total')
        shopping_list = ['Список покупок: ', ]
        for num, i in enumerate(ingredients):
            shopping_list.append(
                f'{num + 1}. {i["name"]} = {i["total"]} {i["measurement"]}'
            )
        text = '\n'.join(shopping_list)
        filename = 'foodgram_shopping_list.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
