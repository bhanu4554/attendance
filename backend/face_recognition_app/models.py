from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class FaceEncoding(models.Model):
    """Store face encodings for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='face_encoding')
    encoding_data = models.TextField()  # JSON string of face encoding array
    confidence_threshold = models.FloatField(default=0.6)
    image_path = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'face_encodings'

    def __str__(self):
        return f"Face encoding for {self.user.username}"

    def set_encoding(self, encoding_array):
        """Convert numpy array to JSON string for storage"""
        self.encoding_data = json.dumps(encoding_array.tolist())

    def get_encoding(self):
        """Convert JSON string back to list for processing"""
        return json.loads(self.encoding_data)


class FaceRecognitionLog(models.Model):
    """Log all face recognition attempts"""
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('no_face', 'No Face Detected'),
        ('multiple_faces', 'Multiple Faces'),
        ('unknown_person', 'Unknown Person'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    confidence_score = models.FloatField(null=True, blank=True)
    image_path = models.CharField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # in seconds

    class Meta:
        ordering = ['-timestamp']
        db_table = 'face_recognition_logs'

    def __str__(self):
        user_str = self.user.username if self.user else 'Unknown'
        return f"{user_str} - {self.status} ({self.timestamp})"