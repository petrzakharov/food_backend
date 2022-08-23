from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from main.models import Follow
from .models import User


class UserUpdatedSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'password',)

    def get_is_subscribed(self, obj):
        return True if Follow.objects.filter(
            author=self.context.get('author'),
            follower=obj.id
        ).exists() else False

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# class UserCreateSerializer(UserCreateSerializer):
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name',
#                   'password')
