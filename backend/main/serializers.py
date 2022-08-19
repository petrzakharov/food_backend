from rest_framework import serializers

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
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get('recipes_limit', None) or 10
        paginated_recipes = obj.recipes.all()[:int(recipes_limit)]
        serializer = RecipeFollowSerializer(paginated_recipes, many=True)
        return serializer.data

    # TODO проверить корректность поля recipes (ошибка при редактировании в админке)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)
        read_only_fields = ('id', 'amount',)

    @staticmethod
    def validate_id(value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError("Передан несуществующий id ингредиента")
        return value


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserUpdatedSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, source='tag')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    text = serializers.CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    @staticmethod
    def get_ingredients(obj):
        return IngredientRecipeSerializer(IngredientAmount.objects.filter(recipe=obj).all(), many=True).data

    def get_is_favorited(self, obj):
        return (
            FavoriteRecipe.objects.filter(recipe=obj, user=self.context.get("request").user).exists() if
            not self.context.get('request').user.is_anonymous else False
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            ShoppingList.objects.filter(recipe=obj, user=self.context.get("request").user).exists() if
            not self.context.get('request').user.is_anonymous else False
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, source='tag', queryset=Tag.objects.all())
    text = serializers.CharField(source='description')
    image = serializers.ImageField(required=False)

    #  TODO убрать required=False из image при тестировании на фронте

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'name', 'text', 'cooking_time', 'image',
        )

    @staticmethod
    def create_ingredient_amount(recipe_instance, ingredients):
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe_instance
            )

    def create(self, validated_data):
        tags = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tag.add(*tags)
        self.create_ingredient_amount(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'tag' in validated_data:
            instance.tag.clear()
            instance.tag.add(*validated_data['tag'])
        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            self.create_ingredient_amount(instance, validated_data['ingredients'])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    @staticmethod
    def validate_ingredients(value):
        if len(value) != len(set(ingredient['id'] for ingredient in value)):
            raise serializers.ValidationError('Ингредиенты должны быть уникальные')
        for ingredient in value:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError('Количество ингредиента должно быть > 0')
        return value

    @staticmethod
    def validate_tags(value):
        if len(value) == 0:
            raise serializers.ValidationError('Количество тегов должно быть > 0')
        return value
