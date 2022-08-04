from django.urls import path, include, re_path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserViewSet


app_name = 'users'


urlpatterns = [
    path('api/users/me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    # переписать


    path('api/users/', UserViewSet.as_view({'post': 'create', 'get': 'list'}), name="users"),
    # переписать для get запроса нужна кастомная вьюха, список всех пользователей с пагинацией
    # для post запроса в принципе должно подходить


    path('api/users/<str:id>/', UserViewSet.as_view({'get': 'retrieve'}), name="users"),
    # переписать, должно возвращать дополнительное поле, подписан ли человек на тебя


    path('api/users/set_password/', UserViewSet.as_view({'post': 'set_password'}), name="set_password"),
    # должно работать из коробки

    path('api/auth/', include('djoser.urls.authtoken')),
    # должно работать из коробки

    path('register/', UserViewSet.as_view({'post': 'create'}), name="register"),
    # del
]

# TODO Проверить ответы сервера по каждому эндпоинту, возможно придется где-то написать свой вьюсет и сериалайзер
# TODO Проверить что правильно установлены пермишены
# https://ifihan.hashnode.dev/customizing-urls-in-djoser