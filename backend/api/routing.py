from django.urls import path

from .consumers import *

websocket_urlpatterns = [
    path('ws/email_letters/', LoadEmailLetterDataConsumer.as_asgi())
]