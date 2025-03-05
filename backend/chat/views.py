from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from .models import ChatRoom, Message, OnlineStatus
from .serializers import ChatRoomSerializer, MessageSerializer, OnlineStatusSerializer

# Create your views here.

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'DOCTOR':
            return ChatRoom.objects.filter(doctor=user)
        elif user.user_type == 'PATIENT':
            return ChatRoom.objects.filter(patient=user)
        return ChatRoom.objects.none()

    def perform_create(self, serializer):
        doctor_id = self.request.data.get('doctor')
        if self.request.user.user_type != 'PATIENT':
            raise ValidationError("Only patients can initiate chat rooms")
        
        # Check if room already exists
        existing_room = ChatRoom.objects.filter(
            doctor_id=doctor_id,
            patient=self.request.user
        ).first()
        
        if existing_room:
            if not existing_room.is_active:
                existing_room.is_active = True
                existing_room.save()
            return existing_room
        
        serializer.save(
            patient=self.request.user,
            doctor_id=doctor_id
        )

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        room = self.get_object()
        messages = Message.objects.filter(room=room).order_by('-timestamp')
        page = self.paginate_queryset(messages)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_messages_read(self, request, pk=None):
        room = self.get_object()
        Message.objects.filter(
            room=room,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({"status": "messages marked as read"})

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            Q(room__doctor=self.request.user) | 
            Q(room__patient=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class OnlineStatusViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OnlineStatusSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.action == 'list':
            # Only get online status for users in active chat rooms
            user = self.request.user
            if user.user_type == 'DOCTOR':
                return OnlineStatus.objects.filter(
                    user__patient_chats__doctor=user,
                    user__patient_chats__is_active=True
                ).distinct()
            elif user.user_type == 'PATIENT':
                return OnlineStatus.objects.filter(
                    user__doctor_chats__patient=user,
                    user__doctor_chats__is_active=True
                ).distinct()