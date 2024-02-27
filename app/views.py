from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import HttpResponseRedirect
from rest_framework import generics, status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, TopicSerializer

from .models import Topic, Category


class CreateUserView(generics.CreateAPIView):
    model = get_user_model()
    serializer_class = UserSerializer


class LoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_profile.html'

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({
                'username': user.username,
                'profile_picture': user.profile_picture.url if user.profile_picture else None,
                'email': user.email
            })
        return Response({'error': 'Invalid Credentials'}, status=401)

    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'username': request.user.username,
                'profile_picture': request.user.profile_picture.url if request.user.profile_picture else None,
                'email': request.user.email
            })
        return HttpResponseRedirect('###')


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
            context = {
                'title': topic['title'],
                'content': topic['content'],
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
    template_name = 'topic.html'


class TopicPagination(PageNumberPagination):
    page_size = 4


class TopicListView(ListAPIView):
    queryset = Topic.objects.all().order_by('-created_at')
    serializer_class = TopicSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'topic_list.html'
    pagination_class = TopicPagination

    def get_queryset(self):
        queryset = Topic.objects.all().order_by('-created_at')
        category_pk = self.kwargs.get('category_pk')
        if category_pk is not None:
            queryset = queryset.filter(category_id=category_pk)
        return queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            'topics': response.data['results'],
            'page': response.data
        }, template_name=self.template_name)


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