from django.urls import path, include
from rest_framework.routers import DefaultRouter

from main.views import TagViewSet, FollowViewSet, IngredientsViewSet, RecipesViewSet, FavoriteRecipeViewSet, \
    ShoppingListViewset

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('users/subscriptions/', FollowViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('users/<int:id>/subscribe/', FollowViewSet.as_view({'post': 'create', 'delete': 'destroy'}), name='subscribe'),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteRecipeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='favorite'
    ),
    path(
        'recipes/<int:id>/shopping_cart/', ShoppingListViewset.as_view({'post': 'create', 'delete': 'destroy'}),
        name='shopping_list'
    ),
    path(
        'recipes/download_shopping_cart', ShoppingListViewset.as_view({'get': 'download'}),
        name='download_shopping_list'
    )
]
