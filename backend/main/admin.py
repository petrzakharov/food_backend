from django.contrib import admin

from .models import Tag, Recipe, Ingredient, IngredientAmount, FavoriteRecipe, ShoppingList, Follow


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    empty_value_display = '-пусто-'
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_follow_recipe',)
    empty_value_display = '-пусто-'
    search_fields = ('name',)

    def author(self, obj):
        return obj.author__name
    # TODO проверить что корректно отображается имя автора

    def count_follow_recipe(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()
    # TODO проверить что работает




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
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientAmount)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingList)
admin.site.register(Follow)
