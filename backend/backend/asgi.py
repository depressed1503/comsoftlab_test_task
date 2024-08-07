import base64
import os

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.asgi import get_asgi_application
from api.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()


class BasicAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Decode credentials from the initial message if sent
        if scope['type'] == 'websocket':
            # Authenticate user from WebSocket messages
            message = await receive()
            if message['type'] == 'websocket.connect':
                headers = dict(scope.get('headers', []))
                auth_header = headers.get(b'authorization', b'').decode('utf-8')

                if auth_header.startswith('Basic '):
                    credentials = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
                    username, password = credentials.split(':', 1)
                    user = await database_sync_to_async(authenticate)(username=username, password=password)
                    scope['user'] = user if user is not None else AnonymousUser()
                else:
                    scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": BasicAuthMiddleware(URLRouter(websocket_urlpatterns))
    }
)