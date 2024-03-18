from django.contrib import admin
from django.urls import path

from app.views import LogoutView, TopicCreateView, TopicListView, TopicDetailView, CommentsView
from app.views import LatestNewsView, UserInfoView, UserRegistrationView, CreateCommentView, LikeCommentView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('profile/', UserInfoView.as_view(), name='profile-page'),
    path('profile/<int:user_id>/', UserInfoView.as_view(), name='others-profile-page'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('topic/create/', TopicCreateView.as_view(), name='create_topic'),
    path('topics/', TopicListView.as_view(), name='topic-list'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
    path('topics/category/<int:category_pk>/', TopicListView.as_view(), name='topic-list-by-category'),
    path('news/last/', LatestNewsView.as_view(), name='last-news'),
    path('comments/create/<int:topic_id>/', CreateCommentView.as_view(), name='create_comment'),
    path('comments/create/<int:topic_id>/<int:parent_id>/', CreateCommentView.as_view(), name='reply_comment'),
    path('comments/topic/<int:topic_id>/', CommentsView.as_view(), name='topic_comments'),
    path('comments/<int:comment_id>/like/', LikeCommentView.as_view(), name='like_comment'),
]
