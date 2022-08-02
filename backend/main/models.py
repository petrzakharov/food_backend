from django.core.validators import MinValueValidator
from django.db import models


class Recipe(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='receipts')
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='pictures/', blank=False, null=False)
    description = models.TextField()
    ingredients = models.ManyToManyField('Ingredient', through='IngredientAmount', related_name='recipes')
    tag = models.ManyToManyField('Tag', related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()
    # как должен формироваться слаг? +
    # добавить при сохранении валидацию code, проверка из какой либо либы с HEX-кодами


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    units = models.CharField(max_length=100)


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey('Ingredient', related_name='ingredient_amount', on_delete=models.PROTECT)
    recipe = models.ForeignKey('Recipe', related_name='ingredient_amount', on_delete=models.PROTECT)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])


class FavoriteRecipe(models.Model):
    user = models.ForeignKey('User', related_name='favorite_recipes', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', related_name='favorite_recipes', on_delete=models.CASCADE)
    # сочетание должно быть уникальнным


class ShoppingList(models.Model):
    user = models.ForeignKey('User', related_name='shopping_list', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', related_name='shoppint_list', on_delete=models.CASCADE)

    #сочетание должно быть уникальным


class Follow(models.Model):
    author = models.ForeignKey('User', related_name='recipe_author', on_delete=models.CASCADE)
    follower = models.ForeignKey('User', related_name='follower', on_delete=models.CASCADE)

    # валидация при сохранении: нельзя подписаться на самого себя
    # сочетание должно быть уникальным




    #
    # class Meta:
    #     ordering = ['-pub_date', ]
    #     verbose_name = 'Рецепт'
    #     verbose_name_plural = 'Рецепты'
    #
    # def __str__(self):
    #     return self.name




    # class Meta:
    #     verbose_name = 'Тег'
    #     verbose_name_plural = 'Теги'
    #
    # def __str__(self):
    #     return self.name