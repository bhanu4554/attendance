from django.urls import path
from .views import (
    FaceEncodingListView,
    FaceRecognitionLogListView,
    register_face,
    recognize_face,
    recognition_stats,
    delete_face_encoding
)

urlpatterns = [
    path('encodings/', FaceEncodingListView.as_view(), name='face-encoding-list'),
    path('logs/', FaceRecognitionLogListView.as_view(), name='face-recognition-logs'),
    path('register/', register_face, name='register-face'),
    path('recognize/', recognize_face, name='recognize-face'),
    path('stats/', recognition_stats, name='recognition-stats'),
    path('delete-encoding/<int:user_id>/', delete_face_encoding, name='delete-face-encoding'),
]