from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipts')
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='pictures/', blank=False, null=False)
    description = models.TextField()
    ingredients = models.ManyToManyField('Ingredient', through='IngredientAmount', related_name='recipes')
    tag = models.ManyToManyField('Tag', related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['-name', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(regex='^#(?:[0-9a-fA-F]{3}){1,2}$', message='Add correct HEX code')]
    )
    slug = models.SlugField()

    class Meta:
        ordering = ['-name', ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    measurement_unit = models.CharField(max_length=100)

    class Meta:
        ordering = ['-name', ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey('Ingredient', related_name='ingredient_amount', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', related_name='ingredient_amount', on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient.name}_{self.amount}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, related_name='favorite_recipes', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', related_name='favorite_recipes', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique favorite recipe')
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user.username}_{self.recipe.name}'


class ShoppingList(models.Model):
    user = models.ForeignKey(User, related_name='shopping_list', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', related_name='shoppint_list', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique recipe in shopping list')
        ]
        verbose_name = 'Шоппинг лист'
        verbose_name_plural = 'Шоппинг лист'

    def __str__(self):
        return f'{self.user.username}_{self.recipe.name}'


class Follow(models.Model):
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'follower'], name='unique_follow')
        ]
        verbose_name = 'Подписчики'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.author.username}_{self.follower.username}'

    def clean(self):
        if self.author == self.follower:
            raise ValidationError(message='You cant follow yourself')
