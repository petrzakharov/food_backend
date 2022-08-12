from django.shortcuts import render, get_object_or_404
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Tag, Follow, Ingredient, Recipe, FavoriteRecipe
from main.serializers import TagSerializer, FollowSerializer, IngredientSerializer, RecipeSerializer, \
    RecipeCreateSerializer, RecipeFollowSerializer
from users.models import User


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FollowViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer

    # TODO добавить поддержку query параметров

    def get_queryset(self):
        followers = Follow.objects.filter(author=self.request.user).values('follower')
        return User.objects.filter(id__in=followers)

    # get_queryset запрашивается когда нужен список объектов
    # когда действия производятся с одним объектом то запрашивается get_object

    def get_serializer_context(self):
        return {
            'author': self.request.user,
        }

    def destroy(self, request, *args, **kwargs):
        queryset = Follow.objects.filter(
            author=self.request.user,
            follower=get_object_or_404(User, id=self.kwargs['id'])
        )
        if queryset.exists():
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = self.get_serializer_context()
        data['follower'] = get_object_or_404(User, id=self.kwargs['id'])
        serializer = self.serializer_class(data=request.data, context=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    # search_fields = ('^name',)

    def get_queryset(self):
        return Ingredient.objects.filter(
            name__istartswith=self.request.query_params.get('name', '')
        )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RecipeCreateSerializer
        return RecipeSerializer


    # TODO добавить фильтрацию по параметрам
    # Создание рецепта
    # Доступно только авторизованному пользователю

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# class FavoriteRecipeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
#     queryset = FavoriteRecipe.objects.all()
#     serializer_class = RecipeFollowSerializer
#
#     def get_object(self):
#         return get_object_or_404(FavoriteRecipe, recipe_id=self.kwargs.get('id'))
#
#     def create(self, request, *args, **kwargs):
#         recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
#         if FavoriteRecipe.objects.filter(recipe=recipe, user=self.request.user).exists():
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         FavoriteRecipe.objects.create(user=self.request.user, recipe=recipe)
#         serializer = self.serializer_class(data=recipe)
#         if serializer.is_valid():
#             #  TODO  тут нужно правильно вернуть сериализованный рецепт
#             return Response(data=serializer.data, status=status.HTTP_201_CREATED)
