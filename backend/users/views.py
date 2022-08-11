from django.shortcuts import render
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from .models import User
from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import UserUpdatedSerializer
from rest_framework.pagination import PageNumberPagination


class UserViewSet(DjoserUserViewSet):

    @action(detail=True, methods=['get'])
    def me(self, request, *args, **kwargs):
        instance = User.objects.get(id=self.request.user.id)
        serializer = UserUpdatedSerializer(instance, context={'author': self.request.user.id})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserUpdatedSerializer(instance, context={'author': self.request.user.id})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = User.objects.all()
        page = self.paginate_queryset(queryset)
        serializer = UserUpdatedSerializer(page, many=True, context={'author': self.request.user.id})
        return self.get_paginated_response(serializer.data)

        # http://www.tomchristie.com/rest-framework-2-docs/api-guide/viewsets
        # https://ilovedjango.com/django/rest-api-framework/views/viewset/
        # https://ifihan.hashnode.dev/customizing-urls-in-djoser
        # TODO Проверить что можно создать пользователя без авторизации