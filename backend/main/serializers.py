from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User
from users.serializers import UserUpdatedSerializer
from .models import Tag, Follow, Ingredient, Recipe, FavoriteRecipe, ShoppingList, IngredientAmount


class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source='code')

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('name', 'image', 'cooking_time')

class FollowSerializer(UserUpdatedSerializer):
    recipes = RecipeFollowSerializer(source='receipts', many=True)
    recipes_count = serializers.SerializerMethodField()

    # TODO дописать после того, как появится вьюха и сериалайзера для Recipes

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')
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

    def get_recipes_count(self, obj):
        return obj.receipts.count()

    # TODO проверить корректность метода get_recipes_count (возможно вынести его в модель)
    # TODO проверить корректность поля recipes (ошибка при редактировании в админке)

class IngredientSerializer(serializers.ModelSerializer):
    # TODO  проблема в этом сериалайзере, непонятно какое поле применять и связывать ли сериалайзер с моделью
    #  сохранение рецепта
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    # class Meta:
    #     # model = Ingredient
    #     fields = ('id', 'amount')

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError("Передан несуществующий id ингредиента")
        return value



class RecipeSerializer(serializers.ModelSerializer):
    author = UserUpdatedSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True, source='tag')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    text = serializers.CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj, user=self.context.get("request").user).exists() if \
            not self.context.get('request').user.is_anonymous else False

    def get_is_in_shopping_cart(self, obj):
        return ShoppingList.objects.filter(recipe=obj, user=self.context.get("request").user).exists() if \
            not self.context.get('request').user.is_anonymous else False


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, source='tag', queryset=Tag.objects.all())
    text = serializers.CharField(source='description')
    image = serializers.ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'name', 'text', 'cooking_time', 'image',
        )

    # def validate_ingredients(value):
    #     for ingredient in value:
    #         if not Ingredient.objects.filter(id=ingredient['id']).exists():
    #             raise serializers.ValidationError("Передан несуществующий id ингредиента")
    #     return value
    #
    # def validate_tags(self, value):
    #     for tag_id in value:
    #         if not Tag.objects.filter(id=tag_id).exists():
    #             raise serializers.ValidationError("Передан несуществующий id тега")
    #     return value

    def create(self, validated_data):
        #  TODO создание должно быть доступно только авторизованному пользователю
        # ingredients = validated_data.pop('ingredients')
        # tags = validated_data.pop('tags')
        # tags = []
        # for tag_id in validated_data.pop('tag'):
        #     tags.append(Tag.objects.get_or_create(id=tag_id))
        tags = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredients')
        # print(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tag.add(*tags)

        # получить ingredient, создать ingredientamount
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        pass
