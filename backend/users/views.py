from django.shortcuts import render
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from .models import User
from rest_framework.response import Response
from rest_framework import generics, status


class UserViewSet(DjoserUserViewSet):

    @action(detail=True, methods=['get'])
    def me(self, request, *args, **kwargs):
        instance = User.objects.get(id=self.request.user.id)
        serializer = UserSerializer(data=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserSerializer(data=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        query_set = User.objects.all()
        return Response(UserSerializer(query_set, many=True).data, status=status.HTTP_200_OK)
        # тут нужна пагинация
        # В сериализаторе нужно доп поле

        # http://www.tomchristie.com/rest-framework-2-docs/api-guide/viewsets
        # https://ilovedjango.com/django/rest-api-framework/views/viewset/
