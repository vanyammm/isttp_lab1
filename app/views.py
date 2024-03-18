from decimal import Decimal
import markdown

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import generics, status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import UserSerializer, TopicSerializer, CommentSerializer

from .models import Topic, Category, CustomUser, Comment, Like


class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "access_token": access_token,
            "refresh_token": str(refresh),
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()


class UserInfoView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_profile.html'
    permission_classes = [AllowAny]

    def get(self, request, user_id=None):
        if user_id is None:
            if request.user.is_authenticated:
                user = request.user
                topics = Topic.objects.filter(created_by_id=user.id).values('id', 'title', 'created_at')
                data = {
                    'username': user.username,
                    'rating': user.rating,
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'email': user.email,
                    'topics': topics
                }
            else:
                data = {'detail': 'User not found or not provided'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            user = get_object_or_404(CustomUser, pk=user_id)
            topics = Topic.objects.filter(created_by_id=user_id).values('id','title', 'created_at')
            data = {
                'username': user.username,
                'rating': user.rating,
                'profile_picture': user.profile_picture.url if user.profile_picture else None,
                'topics': topics
            }

        return Response(data)


class LogoutView(APIView):

    def post(self, request):
        logout(request)
        return Response({"message": "logged out"}, status=status.HTTP_200_OK)


class TopicCreateView(generics.CreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'topic.html'

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super(TopicCreateView, self).create(request, *args, **kwargs)
        if response.status_code == 201:
            topic = response.data
            category = Category.objects.get(pk=topic['category'])
            html_content = markdown.markdown(topic['content'])
            context = {
                'title': topic['title'],
                'content': html_content,
                'category_name': category.name,
                'created_by_username': request.user.username,
                'formatted_created_at': topic['formatted_created_at']
            }
            return Response(context, template_name=self.template_name)
        return response


class TopicDetailView(RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [AllowAny]
    template_name = 'topic.html'


class TopicPagination(PageNumberPagination):
    page_size = 4

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'topics': data  # Важно, чтобы ключ 'topics' использовался в шаблоне
        })


class TopicListView(ListAPIView):
    serializer_class = TopicSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'topic_list.html'
    permission_classes = [AllowAny]
    pagination_class = TopicPagination

    def get_queryset(self):
        category_pk = self.kwargs.get('category_pk')
        if category_pk is None:
            queryset = Topic.objects.all().order_by('-created_at')[:4]
            print("Last topics queryset:", queryset)  # Добавить для отладки
        else:
            queryset = Topic.objects.filter(category_id=category_pk).order_by('-created_at')
            print("Category queryset:", queryset)  # Добавить для отладки
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Если параметр категории не передан, не используем пагинацию
        if 'category_pk' not in self.kwargs:
            serializer = self.get_serializer(queryset, many=True)
            return Response({'topics': serializer.data})  # Обертываем в словарь

        # Использование пагинации для категорий
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # Используем метод класса пагинации

        serializer = self.get_serializer(queryset, many=True)
        return Response({'topics': serializer.data})


class LatestNewsView(ListAPIView):
    serializer_class = TopicSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'latest_news.html'

    def get_queryset(self):
        return Topic.objects.filter(category__pk=1).order_by('-created_at')[:2]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        data = {
            'topics': response.data if isinstance(response.data, list) else [],
        }
        return Response(data, template_name=self.template_name)


class CreateCommentView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        topic_id = self.kwargs.get('topic_id')
        topic = get_object_or_404(Topic, pk=topic_id)
        serializer.save(user=self.request.user, topic_id=topic)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            comment = Comment.objects.get(pk=response.data['id'])
            html = render_to_string('comment_partial.html', {'comment': comment})
            return Response(html, content_type='text/html')
        else:
            return response


class CommentsView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'comments.html'
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        topic_id = self.kwargs.get('topic_id')
        comments = Comment.objects.filter(topic_id=topic_id).order_by('posted_at')
        return Response({'comments': comments})


class LikeCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        like, created = Like.objects.get_or_create(com_id=comment, liked_by_id=request.user)
        author = comment.user

        if created:
            author.rating += Decimal('0.05')
            author.save(update_fields=['rating'])
            print(f"Рейтинг пользователя {author.username} после лайка: {author.rating}")
            return Response({'status': 'like added'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            author.rating -= Decimal('0.05')
            author.save(update_fields=['rating'])
            print(f"Рейтинг пользователя {author.username} после лайка: {author.rating}")
            return Response({'status': 'like removed'}, status=status.HTTP_204_NO_CONTENT)
