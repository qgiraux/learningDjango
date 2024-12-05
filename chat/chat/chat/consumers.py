import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
import asyncio
from urllib.parse import parse_qs
from django.conf import settings

logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis(host='redis', port=6379, db=1)

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Extract the token from the query string
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            # Decode the token to get user_id and nickname
            user_info = self.decode_token(token)
            if user_info:
                self.user_id = user_info['user_id']
                self.nickname = user_info['nickname']
            else:
                self.user_id = None
                self.nickname = "Guest"
        else:
            logger.error("No token provided")
            self.user_id = None
            self.nickname = "Guest"

        # Determine the group name based on whether the user is authenticated or not
        if self.user_id:
            self.group_name = f"user_{self.user_id}"

            # Add the user to the group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.channel_layer.group_add(
                'global_chat',
                self.channel_name
            )
            
            redis_client.hset('global', self.user_id, self.nickname)  # Add user to global hash with nickname
            await self.accept()
        else:
            self.group_name = None
            await self.close()

    def decode_token(self, token):
        import jwt
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return {
                'user_id': decoded.get('user_id', -1),
                'nickname': decoded.get('nickname', 'User')
            }
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            return None

    async def disconnect(self, close_code):
        # Remove the user from the group
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        if self.user_id is not None:
            redis_client.hdel('global', self.user_id)  # Remove user from global hash

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        # Set the sender's name (authenticated user or Guest)
        sender_name = self.nickname

        # Handle different message types
        if message_type == 'chat':
            # Send the message to the group
            await self.channel_layer.group_send(
                'global_chat',
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'sender': sender_name,
                    'group': self.group_name,
                }
            )
        elif message_type == 'game':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'game_info',
                    'message': data['type'],
                    'sender': sender_name,
                    'group': self.group_name,
                }
            )

    async def chat_message(self, event):
        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': 'type: ' + event['type'] + ' message: ' + event['message'] + ' group: ' + event['group'],
            'sender': event['sender'],
        }))
    
    async def game_info(self, event):
        # Send the message to the WebSocket
        for i in range(1):
            await self.send(text_data=json.dumps({
            'type': 'game_info',
            'message': 'type: ' + event['type'] + ' message: ' + event['message'] + ' group: ' + event['group'],
            'sender': event['sender'],
            }))
            await asyncio.sleep(0.2)