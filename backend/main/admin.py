from django.contrib import admin

from .models import Tag, Recipe, Ingredient, IngredientAmount, FavoriteRecipe, ShoppingList, Follow


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_follow_recipe')
    search_fields = ('name',)
    list_filter = ('name', 'author__username', 'tag')

    def author(self, obj):
        return obj.author.username
    # TODO проверить что корректно отображается имя автора

    def count_follow_recipe(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()
    # TODO проверить что работает


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'follower')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)

# Модель рецептов:
# В списке рецептов вывести название и автора рецепта.
# Добавить фильтры по автору, названию рецепта, тегам.
# На странице рецепта вывести общее число добавлений этого рецепта в избранное.
#

#
# Модель пользователей:
# Добавить фильтр списка по email и имени пользователя.


#
# Модель ингредиентов:
# В список вывести название ингредиента и единицы измерения.
# Добавить фильтр по названию.



admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Follow, FollowAdmin)
