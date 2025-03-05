from rest_framework import serializers
from .models import ChatRoom, Message, OnlineStatus
from users.serializers import UserSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(read_only=True)
    patient = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ('id', 'doctor', 'patient', 'created_at', 'is_active')
        read_only_fields = ('created_at',)

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ('id', 'room', 'sender', 'content', 'timestamp', 'is_read')
        read_only_fields = ('timestamp',)

class OnlineStatusSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = OnlineStatus
        fields = ('id', 'user', 'is_online', 'last_activity')
        read_only_fields = ('last_activity',) 