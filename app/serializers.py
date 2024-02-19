from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Topic

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_staff', 'is_superuser')
        extra_kwargs = {'password': {'write_only': True},
                        'is_staff': {'read_only': True},
                        'is_superuser': {'read_only': True}}

    def create(self, validated_data):
        validated_data['is_staff'] = False
        validated_data['is_superuser'] = False
        user = User.objects.create_user(**validated_data)
        return user


class TopicSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by_id.username', read_only=True)
    formatted_created_at = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['pk', 'title', 'category', 'content', 'category_name', 'created_by_username', 'formatted_created_at']

    def get_formatted_created_at(self, obj):
        return obj.created_at.strftime('%d.%m.%y %H:%M')
