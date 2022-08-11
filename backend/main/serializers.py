from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User
from users.serializers import UserUpdatedSerializer
from .models import Tag, Follow, Ingredient, Recipe, FavoriteRecipe, ShoppingList


class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source='code')

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class FollowSerializer(UserUpdatedSerializer):
    # recipes =
    # recipes_count =

    # TODO дописать после того, как появится вьюха и сериалайзера для Recipes

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed',)
        read_only_fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'password',)

    def create(self, validated_data):
        if Follow.objects.filter(**self.context).exists():
            raise serializers.ValidationError({'detail': 'Подписка уже существует'})
        Follow.objects.create(**self.context)
        return User.objects.get(id=self.context['follower'].id)

    def validate(self, data):
        if self.context['author'] == self.context['follower']:
            raise serializers.ValidationError({'detail': 'Нельзя подписаться на самого себя'})
        return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserUpdatedSerializer()
    ingredients = IngredientSerializer(many=True)
    tag = TagSerializer(many=True)  # нужно переименовать в tags
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    text = serializers.CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tag', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj, user=self.context.get("request").user).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingList.objects.filter(recipe=obj, user=self.context.get("request").user).exists()

