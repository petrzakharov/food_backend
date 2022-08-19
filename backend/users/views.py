from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from main.utils import CustomSetPagination
from .models import User
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserUpdatedSerializer


class UserViewSet(DjoserUserViewSet):
    pagination_class = CustomSetPagination
    # OK
    def get_permissions(self):
        if self.action == 'list':
            return AllowAny(),
        return super().get_permissions()

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
