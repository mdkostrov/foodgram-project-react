from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AddRecipeSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipePreviewSerializer, SubscriptionSerializer,
                          TagSerializer)


class SubscriptionView(GenericAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = FoodgramPagination
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class FollowView(APIView):
    pagination_class = FoodgramPagination
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = self.request.user
        data = {'following': author.id, 'user': user.id}
        serializer = FollowSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        if Follow.objects.filter(user=request.user, following=author).exists():
            subscription = get_object_or_404(
                Follow, user=request.user, following=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = FoodgramPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return AddRecipeSerializer

    @staticmethod
    def create_obj(request, pk, model, serializer):
        recipe = get_object_or_404(Recipe, pk=pk)
        if model.objects.filter(recipe=recipe, user=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model(recipe=recipe, user=request.user).save()
        serializer = serializer(get_object_or_404(Recipe, id=pk),
                                context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_obj(request, pk, model):
        if model.objects.filter(recipe=pk, user=request.user).exists():
            get_object_or_404(model, recipe=pk, user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return RecipeViewSet.create_obj(
            request, pk, Favorite, RecipePreviewSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return RecipeViewSet.delete_obj(request, pk, Favorite)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return RecipeViewSet.create_obj(
            request, pk, ShoppingCart, RecipePreviewSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return RecipeViewSet.delete_obj(request, pk, ShoppingCart)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).order_by(
            'name'
        ).annotate(total=Sum('ingredients_list__amount'))
        shopping_list = ['Список покупок: ', ]
        for num, _ in enumerate(ingredients):
            shopping_list.append(
                f'{num + 1}. {_["name"]} = {_["total"]} {_["measurement"]}'
            )
        text = '\n'.join(shopping_list)
        filename = 'foodgram_shopping_list.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
