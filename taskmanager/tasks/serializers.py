from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    completed_at = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = ['id', 'owner', 'title', 'description', 'due_date', 'priority', 'status', 'completed_at', 'created_at']

    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return value

    def validate(self, data):
        # Check if we are updating an existing instance
        if self.instance:
            # If the task is already completed
            if self.instance.status == 'Completed':
                # If they are not reverting status to Pending, block the edit
                new_status = data.get('status')
                if new_status != 'Pending':
                    raise serializers.ValidationError("Cannot edit a completed task unless you revert status to Pending.")
        return data