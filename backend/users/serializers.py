from rest_framework import serializers

from main.models import Follow
from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return True if Follow.objects.filter(
            author=self.context.get('author'),
            follower=obj.id
        ).exists() else False
