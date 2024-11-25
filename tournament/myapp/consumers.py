import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class ClockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.send_time_task = asyncio.create_task(self.send_time())

    async def disconnect(self, close_code):
        self.send_time_task.cancel()

    async def send_time(self):
        while True:
            now = datetime.now()
            # Format time as '%Y-%m-%d %H:%M:%S.%f' and then limit it to 1/100th of a second
            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S.') + f"{now.microsecond // 10000:02d}"
            await self.send(text_data=json.dumps({
                'message': formatted_time
            }))
            await asyncio.sleep(0.01)  # Sleep for 10 milliseconds to update every 1/100th of a second

    async def receive(self, text_data):
        pass