from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    CurrentUserView,
    user_stats
)

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('profile/', CurrentUserView.as_view(), name='current-user'),
    path('stats/', user_stats, name='user-stats'),
]