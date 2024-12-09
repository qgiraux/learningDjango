import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from asgiref.sync import sync_to_async

REDIS_HOST = 'redis'
REDIS_PORT = 6379

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id  # Assuming user authentication is in place
        self.notification_channel = f"user:{self.user_id}:notifications"

        # Subscribe to Redis channel
        self.redis = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.notification_channel)

        await self.accept()

    async def disconnect(self, close_code):
        # Unsubscribe and clean up
        if self.pubsub:
            self.pubsub.unsubscribe(self.notification_channel)

    async def receive(self, text_data):
        # Handle messages received from the WebSocket if needed
        pass

    async def notify_user(self, message):
        # Forward Redis notification to the WebSocket
        await self.send(text_data=json.dumps(message))

    async def listen_to_redis(self):
        # Listen for Redis messages and send them to WebSocket
        for message in self.pubsub.listen():
            if message["type"] == "message":
                await self.notify_user(json.loads(message["data"]))
