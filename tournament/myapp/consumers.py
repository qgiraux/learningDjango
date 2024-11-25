import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

class ClockConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Add this connection to the "clock" group
        await self.channel_layer.group_add(
            "clock",  # Group name
            self.channel_name  # Unique channel name for this connection
        )

        # Increment the client counter in Redis
        await self.increment_client_count()

        # Broadcast the updated client count
        await self.broadcast_client_count()

        # Accept the WebSocket connection
        await self.accept()

        # Start sending time to this client
        self.send_time_task = asyncio.create_task(self.send_time())

    async def disconnect(self, close_code):
        # Remove this connection from the "clock" group
        await self.channel_layer.group_discard(
            "clock",  # Group name
            self.channel_name  # Unique channel name for this connection
        )

        # Decrement the client counter in Redis
        await self.decrement_client_count()

        # Broadcast the updated client count
        await self.broadcast_client_count()

        # Cancel the time-sending task
        self.send_time_task.cancel()

    async def send_time(self):
        while True:
            now = datetime.now()
            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S.') + f"{now.microsecond // 10000:02d}"
            await self.send(text_data=json.dumps({
                'message': formatted_time  # Send the time to the client
            }))
            await asyncio.sleep(0.01)  # Sleep for 1/100th of a second

    async def receive(self, text_data):
        pass  # No data received from client

    async def broadcast_client_count(self):
        """
        Broadcast the number of connected clients to all clients in the group.
        """
        client_count = await self.get_client_count()

        await self.channel_layer.group_send(
            "clock",  # Group name
            {
                "type": "client_count_update",  # Custom message type
                "count": client_count  # Send the client count
            }
        )

    async def client_count_update(self, event):
        """
        Handle the client count update message from the group and send it to the client.
        """
        count = event['count']
        await self.send(text_data=json.dumps({
            'client_count': count  # Send the client count to the WebSocket client
        }))

    @database_sync_to_async
    def increment_client_count(self):
        """
        Increment the client count in Redis.
        """
        channel_layer = get_channel_layer()
        channel_layer.set("connected_clients", int(channel_layer.get("connected_clients") or 0) + 1)

    @database_sync_to_async
    def decrement_client_count(self):
        """
        Decrement the client count in Redis.
        """
        channel_layer = get_channel_layer()
        channel_layer.set("connected_clients", int(channel_layer.get("connected_clients") or 0) - 1)

    @database_sync_to_async
    def get_client_count(self):
        """
        Get the client count from Redis.
        """
        channel_layer = get_channel_layer()
        return int(channel_layer.get("connected_clients") or 0)
