from django.contrib import admin

from .models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    empty_value_display = '-пусто-'
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Tag, TagAdmin)
