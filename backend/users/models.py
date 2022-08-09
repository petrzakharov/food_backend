from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name']
    USERNAME_FIELD = 'email'

    # def is_subscribed(self):
    #     return True if Follow.objects.filter(author=self).exists() else False
