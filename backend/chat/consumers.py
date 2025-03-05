import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, OnlineStatus

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Set user online status
        await self.set_online_status(True)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Set user offline status
        await self.set_online_status(False)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database
        await self.save_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': self.user.id,
                'sender_name': f"{self.user.first_name} {self.user.last_name}"
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name']
        }))

    @database_sync_to_async
    def save_message(self, message):
        chat_room = ChatRoom.objects.get(id=self.room_id)
        Message.objects.create(
            room=chat_room,
            sender=self.user,
            content=message
        )

    @database_sync_to_async
    def set_online_status(self, is_online):
        OnlineStatus.objects.update_or_create(
            user=self.user,
            defaults={'is_online': is_online}
        )

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.set_online_status(True)
        await self.channel_layer.group_add('online_status', self.channel_name)

    async def disconnect(self, close_code):
        await self.set_online_status(False)
        await self.channel_layer.group_discard('online_status', self.channel_name)

    @database_sync_to_async
    def set_online_status(self, is_online):
        OnlineStatus.objects.update_or_create(
            user=self.scope['user'],
            defaults={'is_online': is_online}
        ) 