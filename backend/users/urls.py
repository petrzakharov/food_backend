from django.urls import path, include
from .views import UserViewSet

app_name = 'users'


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('users/<str:id>/', UserViewSet.as_view({'get': 'retrieve'}), name="users"),
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'}), name="set_password"),
    path('users/', UserViewSet.as_view({'post': 'create', 'get': 'list'}), name="users"),
]
