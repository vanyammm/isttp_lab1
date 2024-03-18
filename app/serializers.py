from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser, Comment


from .models import Topic


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'password', 'email', 'is_staff', 'is_superuser')
#         extra_kwargs = {'password': {'write_only': True},
#                         'is_staff': {'read_only': True},
#                         'is_superuser': {'read_only': True}}
#
#     def create(self, validated_data):
#         validated_data['is_staff'] = False
#         validated_data['is_superuser'] = False
#         user = User.objects.create_user(**validated_data)
#         return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TopicSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by_id.username', read_only=True)
    formatted_created_at = serializers.SerializerMethodField()

    created_by_id = serializers.IntegerField(source='created_by.id', read_only=True)
    category_id = serializers.ReadOnlyField(source='category.id')

    class Meta:
        model = Topic
        fields = [
            'pk', 'title', 'content', 'category_name', 'created_by_username',
            'formatted_created_at', 'created_by_id', 'category_id'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by_id'] = instance.created_by_id.id
        representation['category_id'] = instance.category.id
        return representation

    def get_formatted_created_at(self, obj):
        print(f"Debug: Created by ID = {obj.created_by_id.id}, Category ID = {obj.category.id}")
        return obj.created_at.strftime('%d.%m.%y %H:%M')


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    like_count = serializers.ReadOnlyField()
    topic_id = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'user_username', 'content', 'posted_at', 'like_count', 'parent', 'topic_id']