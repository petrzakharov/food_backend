from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'username', 'email',)
    search_fields = ('name', )
    list_filter = ('email', 'username',)


admin.site.register(User, UserAdmin)
