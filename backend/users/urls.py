from django.urls import path, include, re_path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserViewSet


app_name = 'users'


urlpatterns = [
    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('users/<str:id>/', UserViewSet.as_view({'get': 'retrieve'}), name="users"),
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'}), name="set_password"),
    path('users/', UserViewSet.as_view({'post': 'create', 'get': 'list'}), name="users"),
    path('auth/', include('djoser.urls.authtoken')),
]
