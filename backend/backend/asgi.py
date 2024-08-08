import base64
import os
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.asgi import get_asgi_application
from api.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django_asgi_app = get_asgi_application()


@database_sync_to_async
def get_user_from_credentials(username, password):
    user = authenticate(username=username, password=password)
    return user if user is not None else AnonymousUser()


class BasicAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            query_params = parse_qs(scope['query_string'].decode())
            username = query_params.get('username', [None])[0]
            password = query_params.get('password', [None])[0]
            print(username, password)
            if username and password:
                user = await get_user_from_credentials(username, password)
                scope['user'] = user
                print(username, password, user)

        return await super().__call__(scope, receive, send)


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": BasicAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    }
)
