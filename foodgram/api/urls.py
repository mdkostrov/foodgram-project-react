from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (FollowView, IngredientViewSet,
                       TagViewSet, RecipeViewSet,
                       SubscriptionView)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/', SubscriptionView.as_view()),
    path('users/<int:pk>/subscribe/', FollowView.as_view()),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]
