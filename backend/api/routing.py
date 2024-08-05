from django.urls import path

from .consumers import *

websocket_urlpatterns = [
    path('ws/email_letters/', LoadEmaiLetterDataConsumer.as_asgi())
]