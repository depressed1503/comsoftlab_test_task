from django.urls import path, include
from rest_framework import routers
from .views import *
from .routing import websocket_urlpatterns

router = routers.SimpleRouter()
router.register(r'letters', EmailLetterViesSet)
router.register(r'files', EmailLetterFileViewSet)

urlpatterns = [
    path('email/', include(router.urls)),
    path('auth/', include('rest_framework.urls'))
] + websocket_urlpatterns
