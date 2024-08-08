import json
import email
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from email.header import decode_header
from email.utils import parsedate_to_datetime
import logging

from django.contrib.auth import authenticate
from .models import EmailLetter, EmailLetterFile
from .serializers import EmailLetterSerializer
from .utils import *
from imap_tools import MailBox

logger = logging.getLogger(__name__)


class LoadEmailLetterDataConsumer(AsyncWebsocketConsumer):
    def get_serialized_email_letter(self, email_letter: EmailLetter):
        return EmailLetterSerializer(email_letter).data

    async def connect(self):
        await self.accept()
        logger.info("WebSocket connection accepted")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code {close_code}")

    def get_all_messages_uids(self):
        return EmailLetter.objects.filter(owner=self.scope['user']).values_list('uid', flat=True)

    async def receive(self, text_data):
        logger.info(f"Received data: {text_data}")
        if text_data == 'start':
            with MailBox(email_adress_to_imap_server(self.scope['user'].email)).login(self.scope['user'].email, self.scope['user'].email_password) as mailbox:
                messages = list(mailbox.fetch())
                for message_i, msg in enumerate(messages):
                    await self.send(text_data=json.dumps({
                        'progress': message_i,
                        'max': len(messages)
                    }))
                    if msg.uid not in await database_sync_to_async(self.get_all_messages_uids)():
                        email_letter, created = await database_sync_to_async(self.save_email_letter)(
                                                    sender=msg.from_,
                                                    subject=msg.subject,
                                                    date_sent=msg.date.date(),
                                                    text=msg.text or msg.html,
                                                    uid=msg.uid,
                                                    owner=self.scope['user']
                                                )
                        if created:
                            for att in msg.attachments:
                                await database_sync_to_async(self.save_email_attachment)(
                                    email_letter, att.filename, att.payload)
                    else:
                        email_letter = await database_sync_to_async(EmailLetter.objects.get)(uid=msg.uid)
                    await self.send(text_data=json.dumps({
                        "data": await database_sync_to_async(self.get_serialized_email_letter)(email_letter),
                        "reverse_progress": len(messages) - message_i - 1
                    }))

    def get_last_message_uid(self):
        last_message = EmailLetter.objects.filter(owner=self.scope['user']).order_by('-date_sent').first()
        return last_message.uid if last_message else None

    def save_email_letter(self, sender, subject, date_sent, text, uid, date_received=None, owner=None):
        email_letter, created = EmailLetter.objects.get_or_create(
            uid=uid,
            defaults={
                'topic': subject,
                'date_sent': date_sent,
                'text': text,
                'date_received': date_received,
                'owner': owner,
                'sender': sender,
            }
        )
        return email_letter, created

    def save_email_attachment(self, email_letter, filename, content):
        from django.core.files.base import ContentFile
        file_content = ContentFile(content, name=filename)
        EmailLetterFile.objects.create(
            email_letter=email_letter,
            name=filename,
            file=file_content
        )
