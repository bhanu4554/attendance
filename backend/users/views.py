from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import User
from .serializers import UserSerializer, UserProfileSerializer

User = get_user_model()


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            # Allow user creation without authentication
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset.order_by('-created_at')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user instance"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only allow users to modify their own profile or admins
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def get_object(self):
        obj = super().get_object()
        # Users can only access their own profile unless they're admin
        if self.request.user.user_type != 'admin' and obj != self.request.user:
            self.permission_denied(self.request)
        return obj


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user statistics"""
    if request.user.user_type != 'admin':
        return Response({'error': 'Admin access required'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    total_users = User.objects.count()
    students = User.objects.filter(user_type='student').count()
    employees = User.objects.filter(user_type='employee').count()
    admins = User.objects.filter(user_type='admin').count()
    active_users = User.objects.filter(is_active=True).count()
    
    return Response({
        'total_users': total_users,
        'students': students,
        'employees': employees,
        'admins': admins,
        'active_users': active_users,
        'inactive_users': total_users - active_users
    })