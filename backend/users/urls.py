from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'users'

urlpatterns = [
    path('users/auth/login/', obtain_auth_token),
]
