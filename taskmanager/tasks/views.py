from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from .permissions import IsOwner

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Allow anyone to sign up (POST), but only authenticated to see/edit
    permission_classes = [permissions.AllowAny] 

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    # Filtering and Sorting
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'due_date']
    ordering_fields = ['due_date', 'priority']
    ordering = ['due_date']

    def get_queryset(self):
        # Ensure users only see their own tasks
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the new task to the logged-in user
        serializer.save(owner=self.request.user)

    # Custom endpoint to toggle completion
    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        task = self.get_object()
        if task.status == 'Pending':
            task.status = 'Completed'
        else:
            task.status = 'Pending'
        task.save()
        return Response({'status': task.status, 'completed_at': task.completed_at})
