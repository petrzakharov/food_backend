from django.contrib import admin

from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'username', 'email',)
    search_fields = ('name', )
    list_filter = ('name', 'email', 'username',)


# admin.site.register(User, UserAdmin)

# TODO Зарегистрировать тут модель пользователя после того, как напишу свою

