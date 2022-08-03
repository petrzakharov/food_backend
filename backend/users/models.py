from django.db import models

from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'