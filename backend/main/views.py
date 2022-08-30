from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q
from main.models import Tag, Follow, Ingredient, Recipe, FavoriteRecipe, ShoppingList, IngredientAmount
from main.serializers import TagSerializer, FollowSerializer, IngredientSerializer, RecipeSerializer, \
    RecipeCreateSerializer, RecipeFollowSerializer
from users.models import User
from .permissions import OwnerOrReadOnly, ReadOnly

from .utils import CustomSetPagination


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    pagination_class = CustomSetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        authors = Follow.objects.filter(follower=self.request.user).values('author')
        return User.objects.filter(id__in=authors)

    def get_serializer_context(self):
        return {
            'follower': self.request.user,
            'request': self.request
        }

    def destroy(self, request, *args, **kwargs):
        queryset = Follow.objects.filter(
            follower=self.request.user,
            author=get_object_or_404(User, id=self.kwargs['id'])
        )
        if queryset.exists():
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = self.get_serializer_context()
        data['author'] = get_object_or_404(User, id=self.kwargs['id'])
        serializer = self.serializer_class(data=request.data, context=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return Ingredient.objects.all()


class RecipesViewSet(viewsets.ModelViewSet):
    # TODO POST доступен только авторизованному пользователю, GET доступен всем, PATCH и DELETE доступно автору (
    #  проверить)
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)
    pagination_class = CustomSetPagination

    def get_queryset(self):
        params = dict(self.request.query_params)
        queryset = Recipe.objects.all()
        is_favorited = self.request.user if params.get('is_favorited', None) else None
        is_in_shopping_cart = self.request.user if params.get('is_in_shopping_cart', None) else None
        tags = list(params.get('tags')) if params.get('tags', None) else []
        queryset = queryset.filter(
            Q(shopping_list__user=is_in_shopping_cart) &
            Q(favorite_recipes__user=is_favorited)
        )
        if tags:
            return queryset.filter(Q(tag__slug__in=tags))
        return queryset

    def get_permissions(self):
        if self.action == 'retrieve':
            return ReadOnly(),
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = RecipeSerializer(instance, context={'request': request})
        return Response(instance_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        instance_serializer = RecipeSerializer(instance, context={'request': request})
        return Response(instance_serializer.data)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = RecipeFollowSerializer
    http_method_names = ['post', 'delete']
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        user = self.request.user
        try:
            FavoriteRecipe.objects.get(recipe=recipe, user=user)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except FavoriteRecipe.DoesNotExist:
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = self.serializer_class(recipe)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        try:
            favorite_recipe = FavoriteRecipe.objects.get(recipe=recipe, user=self.request.user)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingListViewset(viewsets.ModelViewSet):
    serializer_class = RecipeFollowSerializer
    queryset = ShoppingList.objects.all()
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete', 'post', 'get']

    def get_object(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('id'))

    def create(self, request, *args, **kwargs):
        recipe = self.get_object()
        try:
            ShoppingList.objects.get(recipe=recipe, user=self.request.user)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ShoppingList.DoesNotExist:
            ShoppingList.objects.create(user=self.request.user, recipe=recipe)
            serializer = self.serializer_class(recipe)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        try:
            shopping_list_obj = ShoppingList.objects.get(recipe=recipe, user=self.request.user)
            shopping_list_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingList.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def download(self, request, *args, **kwargs):
        summarized_ingredients = dict()
        ingredients = IngredientAmount.objects.filter(recipe__shopping_list__user=self.request.user).select_related(
            'ingredient')
        for ingredient_amount in ingredients:
            if ingredient_amount.ingredient.name in summarized_ingredients:
                summarized_ingredients[ingredient_amount.ingredient.name][0] += ingredient_amount.amount
            else:
                summarized_ingredients[ingredient_amount.ingredient.name] = [
                    ingredient_amount.amount, ingredient_amount.ingredient.measurement_unit
                ]
        lines = []
        for ingredient_name, amount in summarized_ingredients.items():
            lines.append(f'Ингредиент: {ingredient_name}, Количество: {amount[0]} {amount[1]}')
        response_content = '\n'.join(lines)
        response = HttpResponse(response_content, content_type="text/plain,charset=utf8")
        response['Content-Disposition'] = 'attachment; filename=shopping_list'
        return response
