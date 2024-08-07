import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .serializers import *
from asgiref.sync import sync_to_async

from .utils import find_last_letter


class LoadEmaiLetterDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        find_last_letter(self.scope['user'])
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if text_data == "start":
            total_items = await self.get_total_items()
            chunk_size = 10
            total_chunks = (total_items // chunk_size) + (1 if total_items % chunk_size else 0)
            for chunk in range(total_chunks):
                data = await self.get_chunk_data(chunk, chunk_size)
                progress = ((chunk + 1) / total_chunks) * 100
                await self.send(text_data=json.dumps({'data': data, 'progress': progress},))
                await asyncio.sleep(0.2)  # Задержка для имитации постепенной загрузки

    @sync_to_async
    def get_total_items(self):
        return EmailLetter.objects.count()

    @sync_to_async
    def get_chunk_data(self, chunk, chunk_size):
        start_index = chunk * chunk_size
        end_index = start_index + chunk_size
        data = EmailLetterSerializer(EmailLetter.objects.filter(sender=self.scope['user'].id)[start_index:end_index], many=True).data
        return data
