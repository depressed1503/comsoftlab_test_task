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
from .utils import email_login

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

        if text_data == "start":
            try:
                imap = email_login(self.scope['user'])
                last_uid = await database_sync_to_async(self.get_last_message_uid)()
                res, messages = imap.uid("search", "ALL")

                if res == 'OK':
                    message_ids = messages[0].split()
                    print(message_ids)
                    if last_uid:
                        try:
                            start_index = message_ids.index(last_uid.encode()) + 1
                        except ValueError:
                            start_index = 0
                        message_ids = message_ids[start_index:]
                    else:
                        start_index = 0

                    for i, msg_id in enumerate(message_ids):
                        await self.send(json.dumps({
                            "progress": i + 1 + start_index,
                            "max": len(message_ids) + start_index
                        }))
                        if msg_id not in await database_sync_to_async(self.get_all_messages_uids)():
                            res, msg_data = imap.uid("fetch", msg_id, "(RFC822)")
                            if res == 'OK':
                                raw_email = msg_data[0][1]
                                message = email.message_from_bytes(raw_email)

                                subject = decode_header(message["Subject"])[0]
                                new_subject = subject[0].decode(subject[1] if subject[1] else 'utf-8') if isinstance(
                                    subject[0], bytes) else subject[0]

                                from_ = email.utils.parseaddr(message.get("From"))[1]
                                date_sent_str = message.get("Date")
                                date_received_str = message.get("Received")

                                date_sent = parsedate_to_datetime(date_sent_str).date() if date_sent_str else None
                                date_received = parsedate_to_datetime(
                                    date_received_str.split(';')[-1].strip()).date() if date_received_str else None

                                text = ""
                                for part in message.walk():
                                    if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
                                        charset = part.get_content_charset() or 'utf-8'
                                        try:
                                            text += part.get_payload(decode=True).decode(charset)
                                        except Exception as e:
                                            logger.error(f"Decoding error: {e}")
                                            text += part.get_payload()
                                print(from_, new_subject, date_sent, date_received, text, msg_id, self.scope['user'])
                                email_letter, created = await database_sync_to_async(self.save_email_letter)(
                                    sender=from_,
                                    subject=new_subject,
                                    date_sent=date_sent,
                                    date_received=date_received,
                                    text=text,
                                    uid=msg_id,
                                    owner=self.scope['user']
                                )
                                if created:
                                    for part in message.walk():
                                        if part.get_content_disposition() == 'attachment':
                                            filename = part.get_filename()
                                            if filename:
                                                decoded_header = decode_header(filename)[0]
                                                new_filename = decoded_header[0].decode(
                                                    decoded_header[1] if decoded_header[1] else 'utf-8') if isinstance(
                                                    decoded_header[0], bytes) else decoded_header[0]
                                                file_content = part.get_payload(decode=True)
                                                await database_sync_to_async(self.save_email_attachment)(
                                                    email_letter, new_filename, file_content)
                                await self.send(text_data=json.dumps({
                                    "data": await database_sync_to_async(self.get_serialized_email_letter)(email_letter),
                                    "reverse_progress": len(message_ids) - i - 1
                                }))
                else:
                    logger.error(f"Error fetching messages: {res}")
            except Exception as e:
                logger.error(f"Error: {e}")


    def get_last_message_uid(self):
        last_message = EmailLetter.objects.filter(owner=self.scope['user']).order_by('-date_sent').first()
        return last_message.uid if last_message else None

    def get_user_messages(self):
        return EmailLetterSerializer(EmailLetter.objects.filter(owner=self.scope['user']).order_by('-date_sent'), many=True).data

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
