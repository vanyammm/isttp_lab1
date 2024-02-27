from django.contrib import admin
from django.urls import path

from app.views import CreateUserView, LoginView, LogoutView, TopicCreateView, TopicListView, TopicDetailView
from app.views import LatestNewsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', CreateUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('topic/create/', TopicCreateView.as_view(), name='create_topic'),
    path('topics/', TopicListView.as_view(), name='topic-list'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
    path('topics/category/<int:category_pk>/', TopicListView.as_view(), name='topic-list-by-category'),
    path('news/last/', LatestNewsView.as_view(), name='last-news')
]
